"""Probe the device via direct SSH to find UDW command alternatives."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import paramiko
from utils.config import cfg


def ssh_run(ssh, cmd, timeout=10):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return out, err


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=cfg.DEVICE_HOST,
    port=cfg.DEVICE_SFTP_PORT,
    username=cfg.DEVICE_SFTP_USER,
    password=cfg.DEVICE_SFTP_PASSWORD,
    timeout=15,
)

probes = [
    # Is runUw available?
    "which runUw 2>/dev/null || echo NOT_FOUND",
    "which runuw 2>/dev/null || echo NOT_FOUND",
    "ls /usr/bin/run* 2>/dev/null",
    "ls /usr/local/bin/run* 2>/dev/null",
    # What listening TCP ports exist (UDW might have its own port)?
    "netstat -tlnp 2>/dev/null | grep LISTEN | head -20",
    # Check for dbus / IPC socket that UDW might use
    "ls /tmp/*.sock /run/*.sock 2>/dev/null | head -10",
    # Try the UDW command directly
    'runUw mainApp "WebSocket PUB_WebSocketState 1"',
    'runuw mainApp "WebSocket PUB_WebSocketState 1"',
    # Check for a uw CLI tool
    "uw --help 2>&1 | head -5",
    "uwcli --help 2>&1 | head -5",
]

for cmd in probes:
    out, err = ssh_run(ssh, cmd)
    print(f"\n=== {cmd} ===")
    if out:
        print(out[:400])
    if err:
        print("ERR:", err[:200])

ssh.close()
