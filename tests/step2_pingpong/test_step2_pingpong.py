import json
import os
import re
import subprocess
import pytest
import paramiko
from utils.config import cfg

STEP2_REMOTE_PATH = "/mnt/rw/.dune/machinedata/log/stratus.step2Response.log"
SIFT2_UDW_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "utils", "sift2_udw_cmd.ps1"
)
POWERSHELL_EXE = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

EXPECTED_PINGPONG_FIELDS = {
    "pingEnabled",
    "pingInterval",
    "maxPingFailuresToReconnect",
    "pongTimeout",
}


def _fetch_step2_json() -> dict:
    """Connect to the device via SFTP and return the parsed Step2Response.json."""
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
        with sftp.open(STEP2_REMOTE_PATH, "r") as remote_file:
            content = remote_file.read()
        sftp.close()
    finally:
        ssh.close()
    return json.loads(content)


def _run_udw_command(command: str, wait_ms: int = 3000) -> str:
    """Type a UDW command into Sift2 and return the response text."""
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
        timeout=30,
    )
    output = result.stdout.strip()
    # Extract the part after "RESPONSE:" marker
    for line in output.splitlines():
        if line.startswith("RESPONSE:"):
            return line[len("RESPONSE:"):].strip()
    return output  # return raw if marker not found


@pytest.mark.smoke
class TestStep2PingPong:
    """Verify that Step2Response.json contains the required ping-pong fields."""

    @pytest.fixture(scope="class")
    def step2_data(self):
        """Fetch Step2Response.json from the device once per class."""
        return _fetch_step2_json()

    def test_tunnel_configuration_present(self, step2_data):
        # Arrange / Act
        tunnel_cfg = step2_data.get("tunnelConfiguration")

        # Assert
        assert tunnel_cfg is not None, (
            "'tunnelConfiguration' key is missing from Step2Response.json"
        )

    def test_websocket_configuration_present(self, step2_data):
        # Arrange
        tunnel_cfg = step2_data.get("tunnelConfiguration", {})

        # Act
        ws_cfg = tunnel_cfg.get("websocketConfiguration")

        # Assert
        assert ws_cfg is not None, (
            "'websocketConfiguration' is missing inside tunnelConfiguration"
        )

    def test_ping_enabled_field_present(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert "pingEnabled" in ws_cfg, (
            "'pingEnabled' field is missing from websocketConfiguration"
        )

    def test_ping_interval_field_present(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert "pingInterval" in ws_cfg, (
            "'pingInterval' field is missing from websocketConfiguration"
        )

    def test_max_ping_failures_field_present(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert "maxPingFailuresToReconnect" in ws_cfg, (
            "'maxPingFailuresToReconnect' field is missing from websocketConfiguration"
        )

    def test_pong_timeout_field_present(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert "pongTimeout" in ws_cfg, (
            "'pongTimeout' field is missing from websocketConfiguration"
        )

    def test_all_pingpong_fields_present(self, step2_data):
        ws_cfg = step2_data.get("tunnelConfiguration", {}).get("websocketConfiguration", {})
        missing = EXPECTED_PINGPONG_FIELDS - set(ws_cfg.keys())
        assert not missing, (
            f"The following ping-pong fields are missing from websocketConfiguration: {missing}"
        )

    def test_ping_enabled_value(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert str(ws_cfg.get("pingEnabled")).lower() == "true", (
            f"Expected pingEnabled='true', got {ws_cfg.get('pingEnabled')!r}"
        )

    def test_ping_interval_is_positive(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert int(ws_cfg.get("pingInterval", 0)) > 0, (
            f"Expected pingInterval > 0, got {ws_cfg.get('pingInterval')!r}"
        )

    def test_pong_timeout_is_positive(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert int(ws_cfg.get("pongTimeout", 0)) > 0, (
            f"Expected pongTimeout > 0, got {ws_cfg.get('pongTimeout')!r}"
        )

    def test_max_ping_failures_is_positive(self, step2_data):
        ws_cfg = step2_data["tunnelConfiguration"]["websocketConfiguration"]
        assert int(ws_cfg.get("maxPingFailuresToReconnect", 0)) > 0, (
            f"Expected maxPingFailuresToReconnect > 0, got {ws_cfg.get('maxPingFailuresToReconnect')!r}"
        )


@pytest.mark.smoke
class TestTunnelPingPongStatus:
    """Step 2 — Verify initial ping-pong tunnel status via Sift2 UDW commands.

    UDW commands:
        WebSocket PUB_getPingPongStatus 1
        WebSocket PUB_getPingPongStatus 2

    Expected: Initially tunnel 1 status should be 'unknown'.
    """

    @pytest.fixture(scope="class")
    def tunnel1_status(self):
        """Run UDW command for tunnel 1 and return raw response."""
        return _run_udw_command("WebSocket PUB_getPingPongStatus 1")

    @pytest.fixture(scope="class")
    def tunnel2_status(self):
        """Run UDW command for tunnel 2 and return raw response."""
        return _run_udw_command("WebSocket PUB_getPingPongStatus 2")

    # ── Tunnel 1 ──────────────────────────────────────────────────────────────

    def test_tunnel1_udw_response_not_empty(self, tunnel1_status):
        # Arrange / Act
        response = tunnel1_status

        # Assert
        assert response, (
            "UDW command 'WebSocket PUB_getPingPongStatus 1' returned no response from Sift2"
        )

    def test_tunnel1_initial_status_is_unknown(self, tunnel1_status):
        # Arrange
        response = tunnel1_status.lower()

        # Assert — initial tunnel state must be 'unknown' before any connection
        assert "unknown" in response, (
            f"Expected tunnel 1 ping-pong status to be 'unknown' initially, "
            f"got: {tunnel1_status!r}"
        )

    # ── Tunnel 2 ──────────────────────────────────────────────────────────────

    def test_tunnel2_udw_response_not_empty(self, tunnel2_status):
        # Arrange / Act
        response = tunnel2_status

        # Assert
        assert response, (
            "UDW command 'WebSocket PUB_getPingPongStatus 2' returned no response from Sift2"
        )

    def test_tunnel2_status_returned(self, tunnel2_status):
        # Assert — any non-empty response confirms the command was processed
        assert len(tunnel2_status) > 0, (
            f"UDW command for tunnel 2 returned empty response: {tunnel2_status!r}"
        )

