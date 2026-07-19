"""Test PUB_WebSocketClose and PUB_SetPingIntervalAndMaxTunnelDuration."""
import time
import paramiko
from utils.config import cfg

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(cfg.DEVICE_HOST, port=cfg.DEVICE_SFTP_PORT,
            username=cfg.DEVICE_SFTP_USER, password=cfg.DEVICE_SFTP_PASSWORD, timeout=10)

def run(cmd):
    _, o, e = ssh.exec_command(f'/core/bin/runUw mainApp "{cmd}"', timeout=10)
    out = o.read().decode(errors="replace").strip()
    err = e.read().decode(errors="replace").strip()
    return out, err

print("=== Force-close test ===")
print(f"T1 before: {run('WebSocket PUB_WebSocketState 1')[0]!r}")
print(f"T2 before: {run('WebSocket PUB_WebSocketState 2')[0]!r}")
print(f"Close T1: {run('WebSocket PUB_WebSocketClose 1')[0]!r}")
print(f"Close T2: {run('WebSocket PUB_WebSocketClose 2')[0]!r}")
time.sleep(2)
print(f"T1 after:  {run('WebSocket PUB_WebSocketState 1')[0]!r}")
print(f"T2 after:  {run('WebSocket PUB_WebSocketState 2')[0]!r}")

print("\n=== PUB_SetPingIntervalAndMaxTunnelDuration (read current) ===")
# Try to read current value - may require args
print(f"SetPing (no args): {run('WebSocket PUB_SetPingIntervalAndMaxTunnelDuration')[0]!r}")

ssh.close()
