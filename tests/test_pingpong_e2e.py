"""
PingPong WebSocket Tunnel — End-to-End Test Suite
==================================================
Combines all 5 steps into a single sequential test case:

  Step 1  Verify ping-pong fields exist in Step2Response.json
  Step 2  Confirm both tunnels are UNKNOWN before any signal
  Step 3  Send device_print + device_scan signals; tunnels become CONNECTED
  Step 4  Ping-pong communication is active on both tunnels per ping interval
  Step 5  Leave printer idle (no signals); tunnels revert to UNKNOWN

Run with:
    .venv\\Scripts\\pytest tests/test_pingpong_e2e.py -v -s
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import paramiko
import pytest

from utils.config import cfg

# ── Shared constants ──────────────────────────────────────────────────────────
STEP2_REMOTE_PATH = "/mnt/rw/.dune/machinedata/log/stratus.step2Response.log"
RUNUW_BIN         = "/core/bin/runUw"       # UDW binary on device

TOKEN_URL   = "https://stage.authz.wpp.api.hp.com/openid/v1/token"
SIGNAL_URL  = (
    "https://signalmgmt.pod1.stage.avatar.ext.hp.com"
    "/avatar/v1/entities/signal/AQAAAAGeh6O7bgAAAAE-SMK9"
)

EXPECTED_PINGPONG_FIELDS = {
    "pingEnabled",
    "pingInterval",
    "maxPingFailuresToReconnect",
    "pongTimeout",
}

PINGPONG_ACTIVE   = "1"
PINGPONG_INACTIVE = "0"

POLL_INTERVAL_SECS = 15        # poll every 15s for faster state-change detection
IDLE_TIMEOUT_BUFFER_SECS = 120 # buffer on top of maxTunnelIdleDuration

# PUB_SetPingIntervalAndMaxTunnelDuration restarts the WebSocket service
# (even on UNKNOWN tunnels) and takes >3 min to recover — do not use.
FORCE_FAST_IDLE_SECS: int | None = None


# ── SSH persistent connection ─────────────────────────────────────────────────

_ssh_client: paramiko.SSHClient | None = None


def _get_ssh() -> paramiko.SSHClient:
    """Return the shared SSH connection, (re)connecting if needed."""
    global _ssh_client
    if _ssh_client is None or not _ssh_client.get_transport() or \
            not _ssh_client.get_transport().is_active():
        if _ssh_client is not None:
            try:
                _ssh_client.close()
            except Exception:
                pass
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=cfg.DEVICE_HOST,
            port=cfg.DEVICE_SFTP_PORT,
            username=cfg.DEVICE_SFTP_USER,
            password=cfg.DEVICE_SFTP_PASSWORD,
            timeout=30,
        )
        _ssh_client = client
    return _ssh_client


# ── Shared helpers ────────────────────────────────────────────────────────────

def _fetch_step2_json() -> dict:
    ssh = _get_ssh()
    sftp = ssh.open_sftp()
    with sftp.open(STEP2_REMOTE_PATH, "r") as f:
        content = f.read()
    sftp.close()
    return json.loads(content)


def _run_udw_command(command: str, timeout: int = 15) -> str:
    """Run a UDW command directly on the device via SSH (no Sift2 needed).

    Uses the persistent SSH connection; reconnects automatically on failure.
    """
    for attempt in range(2):
        try:
            ssh = _get_ssh()
            shell_cmd = f'{RUNUW_BIN} mainApp "{command}"'
            _, stdout, _ = ssh.exec_command(shell_cmd, timeout=timeout)
            return stdout.read().decode(errors="replace").strip()
        except Exception:
            # Force reconnect on next attempt
            global _ssh_client
            _ssh_client = None
            if attempt == 0:
                time.sleep(3)
    return ""



def _extract_status_value(response: str) -> str:
    """Extract '0' or '1' from the UDW PingPongStatus response.

    With direct SSH the response is a clean '0' or '1'.
    """
    import re
    val = response.strip().split()[0] if response.strip() else ""
    if val in ("0", "1"):
        return val
    m = re.search(r"#:([01])\b", response)
    return m.group(1) if m else response.strip()


_WS_KNOWN_STATES = ("CONNECTED", "UNKNOWN", "OPEN", "CLOSED", "CONNECTING", "CLOSING")


def _get_websocket_state(tunnel: int, retries: int = 3) -> str:
    """Return the WebSocketState string (e.g. 'CONNECTED', 'UNKNOWN') via SSH."""
    for attempt in range(retries):
        raw = _run_udw_command(f"WebSocket PUB_WebSocketState {tunnel}")
        candidate = raw.strip().upper().split()[0] if raw.strip() else ""
        if candidate in _WS_KNOWN_STATES:
            return candidate
        if attempt < retries - 1:
            time.sleep(3)
    return ""  # all retries exhausted


def _get_access_token() -> str:
    ctx  = ssl._create_unverified_context()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req  = urllib.request.Request(
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
    ctx     = ssl._create_unverified_context()
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


def _poll_until_unknown(tunnel: int, timeout_secs: int) -> tuple[str, float]:
    """Poll WebSocketState every POLL_INTERVAL_SECS until UNKNOWN or timeout.

    SSH errors during polling are caught and retried after a short delay so
    a transient network hiccup doesn't abort the whole idle-wait.
    Returns (final_state, elapsed_seconds).
    """
    start    = time.monotonic()
    deadline = start + timeout_secs
    try:
        state = _get_websocket_state(tunnel)
    except Exception:
        state = ""
    elapsed = 0.0

    while time.monotonic() < deadline:
        if state == "UNKNOWN":
            break
        time.sleep(POLL_INTERVAL_SECS)
        elapsed = time.monotonic() - start
        try:
            new_state = _get_websocket_state(tunnel)
            if new_state:
                state = new_state
        except Exception:
            pass   # transient SSH error — keep last known state, keep polling

    return state, elapsed


# ══════════════════════════════════════════════════════════════════════════════
# Combined E2E — all 5 steps in a single test case
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.smoke
class TestPingPongE2E:
    """Full end-to-end PingPong WebSocket test.

    Executes all 5 steps sequentially inside one test method so a single
    pass/fail result is reported for the entire flow:

      Step 1  Verify ping-pong fields exist in Step2Response.json
      Step 2  Confirm both tunnels are UNKNOWN before any signal
      Step 3  Send device_print + device_scan; tunnels become CONNECTED
      Step 4  Ping-pong is active on both tunnels per ping interval
      Step 5  Leave printer idle; tunnels revert to UNKNOWN
    """

    def test_full_pingpong_e2e(self):
        # ── Step 1: Verify ping-pong fields in Step2Response.json ─────────────
        print("\n[Step 1] Fetching Step2Response.json from device …")
        step2_data = _fetch_step2_json()

        tunnel_cfg = step2_data.get("tunnelConfiguration")
        assert tunnel_cfg is not None, (
            "'tunnelConfiguration' key missing from Step2Response.json"
        )

        ws_cfg = tunnel_cfg.get("websocketConfiguration")
        assert ws_cfg is not None, (
            "'websocketConfiguration' missing inside tunnelConfiguration"
        )

        missing = EXPECTED_PINGPONG_FIELDS - set(ws_cfg.keys())
        assert not missing, (
            f"Missing ping-pong fields in websocketConfiguration: {missing}"
        )

        assert str(ws_cfg.get("pingEnabled")).lower() == "true", (
            f"Expected pingEnabled='true', got {ws_cfg.get('pingEnabled')!r}"
        )

        ping_interval = int(ws_cfg.get("pingInterval", 0))
        assert ping_interval > 0, (
            f"Expected pingInterval > 0, got {ws_cfg.get('pingInterval')!r}"
        )
        assert ping_interval == 15, (
            f"Expected pingInterval=15s, got {ping_interval}"
        )

        pong_timeout = int(ws_cfg.get("pongTimeout", 0))
        assert pong_timeout > 0, (
            f"Expected pongTimeout > 0, got {ws_cfg.get('pongTimeout')!r}"
        )

        max_ping_failures = int(ws_cfg.get("maxPingFailuresToReconnect", 0))
        assert max_ping_failures > 0, (
            f"Expected maxPingFailuresToReconnect > 0, got "
            f"{ws_cfg.get('maxPingFailuresToReconnect')!r}"
        )

        max_idle_secs = int(tunnel_cfg.get("maxTunnelIdleDuration", 0))
        assert max_idle_secs == 600, (
            f"Expected maxTunnelIdleDuration=600s, got {max_idle_secs}"
        )
        print("[Step 1] PASSED — all ping-pong config fields present and valid.")

        # ── Step 2: Both tunnels must be UNKNOWN before any signal ────────────
        # If a previous run left the tunnels CONNECTED, wait for idle timeout
        # before proceeding — otherwise the signal test won't show a transition.
        print("\n[Step 2] Checking initial WebSocket tunnel states …")
        t1_initial = _get_websocket_state(1)
        t2_initial = _get_websocket_state(2)

        if t1_initial == "CONNECTED" or t2_initial == "CONNECTED":
            print(f"[Step 2] Tunnels still CONNECTED from a previous run "
                  f"(T1={t1_initial}, T2={t2_initial}). Force-closing …")
            if t1_initial == "CONNECTED":
                _run_udw_command("WebSocket PUB_WebSocketClose 1")
            if t2_initial == "CONNECTED":
                _run_udw_command("WebSocket PUB_WebSocketClose 2")
            time.sleep(3)  # allow state to update after close
            t1_initial = _get_websocket_state(1)
            t2_initial = _get_websocket_state(2)
            print(f"[Step 2] After force-close: T1={t1_initial}, T2={t2_initial}")

        assert t1_initial in ("UNKNOWN", ""), (
            f"Tunnel 1 expected UNKNOWN before any signal, got: '{t1_initial}'"
        )
        assert t2_initial in ("UNKNOWN", ""), (
            f"Tunnel 2 expected UNKNOWN before any signal, got: '{t2_initial}'"
        )
        print(f"[Step 2] PASSED — Tunnel 1: '{t1_initial or 'no-response'}', "
              f"Tunnel 2: '{t2_initial or 'no-response'}' (not CONNECTED).")

        # ── Step 3: Send signals; tunnels become CONNECTED ────────────────────
        print("\n[Step 3] Sending device_print and device_scan signals …")
        token        = _get_access_token()
        print_status = _send_signal("device_print", token)
        scan_status  = _send_signal("device_scan",  token)

        assert print_status == 202, (
            f"device_print signal expected HTTP 202, got {print_status}"
        )
        assert scan_status == 202, (
            f"device_scan signal expected HTTP 202, got {scan_status}"
        )

        print("[Step 3] Signals accepted (HTTP 202). Waiting for tunnels to become CONNECTED …")
        # Poll until both tunnels are CONNECTED (device may take 20–60 s)
        connect_timeout = 120
        connect_deadline = time.monotonic() + connect_timeout
        t1_connected = t2_connected = ""
        while time.monotonic() < connect_deadline:
            time.sleep(5)
            t1_connected = _get_websocket_state(1)
            t2_connected = _get_websocket_state(2)
            print(f"  T1={t1_connected} T2={t2_connected}")
            if t1_connected == "CONNECTED" and t2_connected == "CONNECTED":
                break

        t1_connected = _get_websocket_state(1)
        t2_connected = _get_websocket_state(2)

        assert t1_connected == "CONNECTED", (
            f"Tunnel 1 expected CONNECTED after signals, got: '{t1_connected}'"
        )
        assert t2_connected == "CONNECTED", (
            f"Tunnel 2 expected CONNECTED after signals, got: '{t2_connected}'"
        )
        print("[Step 3] PASSED — both tunnels are CONNECTED.")

        # ── Step 4: Ping-pong active before and after one ping interval ───────
        # Wait one full ping interval first — ping-pong becomes active only after
        # the first ping/pong exchange completes (up to pingInterval seconds).
        print(f"\n[Step 4] Checking ping-pong status (pingInterval={ping_interval}s) …")
        print(f"[Step 4] Waiting {ping_interval}s for first ping cycle to complete …")
        time.sleep(ping_interval)

        t1_before = _extract_status_value(
            _run_udw_command("WebSocket PUB_getPingPongStatus 1")
        )
        t2_before = _extract_status_value(
            _run_udw_command("WebSocket PUB_getPingPongStatus 2")
        )

        assert t1_before == PINGPONG_ACTIVE, (
            f"Tunnel 1 ping-pong not active at T={ping_interval}s: got '{t1_before}'"
        )
        assert t2_before == PINGPONG_ACTIVE, (
            f"Tunnel 2 ping-pong not active at T={ping_interval}s: got '{t2_before}'"
        )

        wait_secs = ping_interval + 2
        print(f"[Step 4] Waiting {wait_secs}s (second ping cycle + buffer) …")
        time.sleep(wait_secs)

        t1_after = _extract_status_value(
            _run_udw_command("WebSocket PUB_getPingPongStatus 1")
        )
        t2_after = _extract_status_value(
            _run_udw_command("WebSocket PUB_getPingPongStatus 2")
        )

        assert t1_after == PINGPONG_ACTIVE, (
            f"Tunnel 1 ping-pong not active after {wait_secs}s: got '{t1_after}'"
        )
        assert t2_after == PINGPONG_ACTIVE, (
            f"Tunnel 2 ping-pong not active after {wait_secs}s: got '{t2_after}'"
        )
        print("[Step 4] PASSED — ping-pong active on both tunnels.")

        # ── Step 5: Idle — tunnels revert to UNKNOWN ──────────────────────────
        timeout = max_idle_secs + IDLE_TIMEOUT_BUFFER_SECS
        print(
            f"\n[Step 5] Leaving device idle; expecting UNKNOWN within {timeout}s …"
        )
        t1_idle, t1_elapsed = _poll_until_unknown(1, timeout)
        t2_idle, t2_elapsed = _poll_until_unknown(2, timeout)

        assert t1_idle == "UNKNOWN", (
            f"Tunnel 1 expected UNKNOWN after {max_idle_secs}s idle "
            f"(waited {t1_elapsed:.0f}s, timeout={timeout}s), got: '{t1_idle}'"
        )
        assert t2_idle == "UNKNOWN", (
            f"Tunnel 2 expected UNKNOWN after {max_idle_secs}s idle "
            f"(waited {t2_elapsed:.0f}s, timeout={timeout}s), got: '{t2_idle}'"
        )
        print("[Step 5] PASSED — both tunnels reverted to UNKNOWN after idle.")
