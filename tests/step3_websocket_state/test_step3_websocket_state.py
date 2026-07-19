import json
import os
import subprocess
import ssl
import time
import urllib.request
import urllib.parse
import pytest
from utils.config import cfg

# ── Constants ─────────────────────────────────────────────────────────────────
TOKEN_URL = "https://stage.authz.wpp.api.hp.com/openid/v1/token"
SIGNAL_URL = (
    "https://signalmgmt.pod1.stage.avatar.ext.hp.com"
    "/avatar/v1/entities/signal/AQAAAAGeh6O7bgAAAAE-SMK9"
)

SIFT2_UDW_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "utils", "sift2_udw_cmd.ps1"
)
POWERSHELL_EXE = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
UDW_WAIT_MS = 8000


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_access_token() -> str:
    """Fetch an OAuth2 bearer token via client_credentials grant."""
    ctx = ssl._create_unverified_context()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + cfg.SIGNAL_CLIENT_CREDENTIALS,
        },
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return json.loads(resp.read())["access_token"]


def _send_signal(signal_type: str, token: str) -> int:
    """PATCH a device signal to the Stratus signal-management service.

    Returns the HTTP status code.  Expected: 202 Accepted.
    """
    ctx = ssl._create_unverified_context()
    payload = json.dumps(
        {"version": "1.0.0", "signal_type": signal_type, "value": True}
    ).encode()
    req = urllib.request.Request(
        SIGNAL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


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


# ── Step 3 Tests ──────────────────────────────────────────────────────────────

@pytest.mark.smoke
class TestStep3WebSocketState:
    """Step 3 — Send print/scan signals and verify WebSocket tunnels become CONNECTED."""

    @pytest.fixture(scope="class")
    def access_token(self):
        """Obtain an OAuth2 bearer token once per class."""
        return _get_access_token()

    @pytest.fixture(scope="class")
    def signals_sent(self, access_token):
        """Send both device_print and device_scan signals, then wait for tunnels to connect."""
        print_status = _send_signal("device_print", access_token)
        scan_status = _send_signal("device_scan", access_token)
        # Allow up to 20 s for the device to establish both WebSocket tunnels
        time.sleep(20)
        return {"device_print": print_status, "device_scan": scan_status}

    # ── Signal tests ──────────────────────────────────────────────────────────

    def test_device_print_signal_accepted(self, signals_sent):
        # Act (signals already sent in fixture)
        status = signals_sent["device_print"]

        # Assert
        assert status == 202, (
            f"device_print signal expected HTTP 202 Accepted but got {status}"
        )

    def test_device_scan_signal_accepted(self, signals_sent):
        # Act (signals already sent in fixture)
        status = signals_sent["device_scan"]

        # Assert
        assert status == 202, (
            f"device_scan signal expected HTTP 202 Accepted but got {status}"
        )

    # ── Tunnel-state tests (run after signals + 20 s wait) ───────────────────

    @pytest.fixture(scope="class")
    def tunnel1_state(self, signals_sent):
        """Fetch WebSocketState for tunnel 1 via Sift2 UDW after signals are sent."""
        return _run_udw_command("WebSocket PUB_WebSocketState 1")

    @pytest.fixture(scope="class")
    def tunnel2_state(self, signals_sent):
        """Fetch WebSocketState for tunnel 2 via Sift2 UDW after signals are sent."""
        return _run_udw_command("WebSocket PUB_WebSocketState 2")

    def test_tunnel1_state_is_connected(self, tunnel1_state):
        # Assert
        assert "CONNECTED" in tunnel1_state.upper(), (
            f"Tunnel 1 expected CONNECTED but got: '{tunnel1_state}'"
        )

    def test_tunnel2_state_is_connected(self, tunnel2_state):
        # Assert
        assert "CONNECTED" in tunnel2_state.upper(), (
            f"Tunnel 2 expected CONNECTED but got: '{tunnel2_state}'"
        )
