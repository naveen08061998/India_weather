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
UDW_WAIT_MS = 8000

# Poll every 60 s; allow up to 2 minutes past the configured idle duration
POLL_INTERVAL_SECS = 60
TIMEOUT_BUFFER_SECS = 120


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_step2_json() -> dict:
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


def _get_websocket_state(tunnel: int) -> str:
    """Return the WebSocketState string for the given tunnel number."""
    raw = _run_udw_command(f"WebSocket PUB_WebSocketState {tunnel}")
    # Extract value after '#:' e.g. '07/06/26-14:17:13 #:UNKNOWN' → 'UNKNOWN'
    for part in raw.split("#:"):
        val = part.strip()
        if val and not val[0].isdigit():
            return val.split()[0].upper()
    return raw.strip().upper()


def _poll_until_unknown(tunnel: int, timeout_secs: int) -> tuple[str, float]:
    """Poll WebSocketState every POLL_INTERVAL_SECS until UNKNOWN or timeout.

    Returns (final_state, elapsed_seconds).
    """
    deadline = time.monotonic() + timeout_secs
    state = _get_websocket_state(tunnel)
    elapsed = 0.0

    while state != "UNKNOWN" and time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SECS)
        elapsed = time.monotonic() - (deadline - timeout_secs)
        state = _get_websocket_state(tunnel)

    return state, elapsed


# ── Step 5 Tests ──────────────────────────────────────────────────────────────

@pytest.mark.smoke
class TestStep5TunnelIdle:
    """Step 5 — Leave the printer idle (no print/scan signals) and verify
    both WebSocket tunnels revert to UNKNOWN within maxTunnelIdleDuration."""

    @pytest.fixture(scope="class")
    def idle_config(self):
        """Read maxTunnelIdleDuration from the device Step2Response config."""
        data = _fetch_step2_json()
        return {
            "max_idle_secs": int(
                data["tunnelConfiguration"]["maxTunnelIdleDuration"]
            ),
        }

    @pytest.fixture(scope="class")
    def idle_tunnel_states(self, idle_config):
        """Wait for both tunnels to go UNKNOWN after the idle period.

        No print/scan signals are sent — the device is left completely idle.
        Polls every 60 s up to (maxTunnelIdleDuration + TIMEOUT_BUFFER_SECS).
        """
        max_idle = idle_config["max_idle_secs"]
        timeout  = max_idle + TIMEOUT_BUFFER_SECS

        t1_state, t1_elapsed = _poll_until_unknown(1, timeout)
        t2_state, t2_elapsed = _poll_until_unknown(2, timeout)

        return {
            "t1_state":   t1_state,
            "t2_state":   t2_state,
            "t1_elapsed": t1_elapsed,
            "t2_elapsed": t2_elapsed,
            "max_idle":   max_idle,
            "timeout":    timeout,
        }

    # ── Config verification ───────────────────────────────────────────────────

    def test_max_tunnel_idle_duration_is_configured(self, idle_config):
        """maxTunnelIdleDuration must be a positive value."""
        assert idle_config["max_idle_secs"] > 0, (
            f"maxTunnelIdleDuration must be > 0, got {idle_config['max_idle_secs']}"
        )

    def test_max_tunnel_idle_duration_value(self, idle_config):
        """maxTunnelIdleDuration should be 600 s (10 minutes) as configured."""
        assert idle_config["max_idle_secs"] == 600, (
            f"Expected maxTunnelIdleDuration=600 but got {idle_config['max_idle_secs']}"
        )

    # ── Idle state assertions ─────────────────────────────────────────────────

    def test_tunnel1_reverts_to_unknown_after_idle(self, idle_tunnel_states):
        """Tunnel 1 must go UNKNOWN after the printer is left idle
        (no eprint/print signal sent) for maxTunnelIdleDuration."""
        s = idle_tunnel_states
        assert s["t1_state"] == "UNKNOWN", (
            f"Tunnel 1 expected UNKNOWN after {s['max_idle']:.0f}s idle "
            f"(waited {s['t1_elapsed']:.0f}s, timeout={s['timeout']}s) "
            f"but got: '{s['t1_state']}'"
        )

    def test_tunnel2_reverts_to_unknown_after_idle(self, idle_tunnel_states):
        """Tunnel 2 must go UNKNOWN after the printer is left idle
        (no eprint/print signal sent) for maxTunnelIdleDuration."""
        s = idle_tunnel_states
        assert s["t2_state"] == "UNKNOWN", (
            f"Tunnel 2 expected UNKNOWN after {s['max_idle']:.0f}s idle "
            f"(waited {s['t2_elapsed']:.0f}s, timeout={s['timeout']}s) "
            f"but got: '{s['t2_state']}'"
        )
