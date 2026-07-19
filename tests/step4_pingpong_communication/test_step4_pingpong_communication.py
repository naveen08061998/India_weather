import json
import os
import subprocess
import time
import pytest
import paramiko
from utils.config import cfg

# ── Constants ─────────────────────────────────────────────────────────────────
STEP2_REMOTE_PATH = "/mnt/rw/.dune/machinedata/log/stratus.step2Response.log"

SIFT2_UDW_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "utils", "sift2_udw_cmd.ps1"
)
POWERSHELL_EXE = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
UDW_WAIT_MS = 5000

# PUB_getPingPongStatus response values
PINGPONG_ACTIVE = "1"    # ping-pong is running on this tunnel
PINGPONG_INACTIVE = "0"  # ping-pong not running (tunnel not connected)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_step2_json() -> dict:
    """Fetch Step2Response.json from the device via SFTP and return parsed JSON."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=cfg.DEVICE_HOST,
        port=cfg.DEVICE_SFTP_PORT,
        username=cfg.DEVICE_SFTP_USER,
        password=cfg.DEVICE_SFTP_PASSWORD,
        timeout=30,
    )
    try:
        sftp = ssh.open_sftp()
        with sftp.open(STEP2_REMOTE_PATH, "r") as f:
            content = f.read()
        sftp.close()
    finally:
        ssh.close()
    return json.loads(content)


def _run_udw_command(command: str, wait_ms: int = UDW_WAIT_MS) -> str:
    """Send a UDW command via Sift2 and return the response text."""
    result = subprocess.run(
        [
            POWERSHELL_EXE,
            "-ExecutionPolicy", "Bypass",
            "-File", os.path.abspath(SIFT2_UDW_SCRIPT),
            "-Command", command,
            "-WaitMs", str(wait_ms),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = result.stdout.strip()
    for line in output.splitlines():
        if line.startswith("RESPONSE:"):
            return line[len("RESPONSE:"):].strip()
    return output


def _extract_status_value(response: str) -> str:
    """Extract the value after '#:' from a UDW response line.

    e.g. '07/06/26-14:17:13 #:1' → '1'
    """
    for part in response.split("#:"):
        val = part.strip().split()[0] if part.strip() else ""
        if val in ("0", "1"):
            return val
    return response.strip()


# ── Step 4 Tests ──────────────────────────────────────────────────────────────

@pytest.mark.smoke
class TestStep4PingPongCommunication:
    """Step 4 — Verify ping-pong communication cycles on both tunnels
    according to the configured ping interval."""

    @pytest.fixture(scope="class")
    def step2_data(self):
        """Fetch Step2Response.json once for the whole class."""
        return _fetch_step2_json()

    @pytest.fixture(scope="class")
    def ping_interval(self, step2_data):
        """Return pingInterval (seconds) from the device configuration."""
        return int(
            step2_data["tunnelConfiguration"]["websocketConfiguration"]["pingInterval"]
        )

    @pytest.fixture(scope="class")
    def pingpong_samples(self, ping_interval):
        """Sample ping-pong status for both tunnels before and after one interval.

        Flow:
          1. Read status for T1 and T2 (T=0).
          2. Wait pingInterval + 2 s so at least one full ping cycle completes.
          3. Read status for T1 and T2 again (T=pingInterval+2).
        Returns dict with before/after values for each tunnel.
        """
        t1_before_raw = _run_udw_command("WebSocket PUB_getPingPongStatus 1")
        t2_before_raw = _run_udw_command("WebSocket PUB_getPingPongStatus 2")

        wait_secs = ping_interval + 2
        time.sleep(wait_secs)

        t1_after_raw = _run_udw_command("WebSocket PUB_getPingPongStatus 1")
        t2_after_raw = _run_udw_command("WebSocket PUB_getPingPongStatus 2")

        return {
            "t1_before": _extract_status_value(t1_before_raw),
            "t2_before": _extract_status_value(t2_before_raw),
            "t1_after":  _extract_status_value(t1_after_raw),
            "t2_after":  _extract_status_value(t2_after_raw),
            "wait_secs": wait_secs,
        }

    # ── Interval config verification ──────────────────────────────────────────

    def test_ping_interval_is_configured(self, ping_interval):
        """Ping interval must be a positive integer (device config is valid)."""
        assert ping_interval > 0, (
            f"pingInterval must be > 0, got {ping_interval}"
        )

    def test_ping_interval_value(self, ping_interval):
        """Ping interval should be 15 seconds as configured in Step2Response."""
        assert ping_interval == 15, (
            f"Expected pingInterval=15 but got {ping_interval}"
        )

    # ── Initial status (T=0) ─────────────────────────────────────────────────

    def test_tunnel1_pingpong_active_at_start(self, pingpong_samples):
        """Tunnel 1 ping-pong must be active (status=1) at the start of observation."""
        assert pingpong_samples["t1_before"] == PINGPONG_ACTIVE, (
            f"Tunnel 1 ping-pong not active at T=0: got '{pingpong_samples['t1_before']}'"
        )

    def test_tunnel2_pingpong_active_at_start(self, pingpong_samples):
        """Tunnel 2 ping-pong must be active (status=1) at the start of observation."""
        assert pingpong_samples["t2_before"] == PINGPONG_ACTIVE, (
            f"Tunnel 2 ping-pong not active at T=0: got '{pingpong_samples['t2_before']}'"
        )

    # ── Status after one full ping interval ──────────────────────────────────

    def test_tunnel1_pingpong_active_after_interval(self, pingpong_samples):
        """Tunnel 1 ping-pong must remain active after one ping interval elapses,
        confirming communication is happening according to the configured interval."""
        assert pingpong_samples["t1_after"] == PINGPONG_ACTIVE, (
            f"Tunnel 1 ping-pong not active after {pingpong_samples['wait_secs']}s "
            f"(one ping interval): got '{pingpong_samples['t1_after']}'"
        )

    def test_tunnel2_pingpong_active_after_interval(self, pingpong_samples):
        """Tunnel 2 ping-pong must remain active after one ping interval elapses,
        confirming communication is happening according to the configured interval."""
        assert pingpong_samples["t2_after"] == PINGPONG_ACTIVE, (
            f"Tunnel 2 ping-pong not active after {pingpong_samples['wait_secs']}s "
            f"(one ping interval): got '{pingpong_samples['t2_after']}'"
        )
