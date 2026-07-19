"""
Probe the UDW TCP socket on the device (mainApp port 6130).
Connect via SSH tunnel, send UDW commands, read responses.
"""
import sys
import os
import socket
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import paramiko
from utils.config import cfg

UDW_PORT = 6130   # mainApp listens here on localhost

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=cfg.DEVICE_HOST,
    port=cfg.DEVICE_SFTP_PORT,
    username=cfg.DEVICE_SFTP_USER,
    password=cfg.DEVICE_SFTP_PASSWORD,
    timeout=15,
)

# Open an SSH tunnel: local port -> device 127.0.0.1:6130
transport = ssh.get_transport()
channel   = transport.open_channel("direct-tcpip",
                                   dest_addr=("127.0.0.1", UDW_PORT),
                                   src_addr=("127.0.0.1", 0))

print(f"Tunnel open to device 127.0.0.1:{UDW_PORT}")

# Read any banner the server sends on connect
channel.settimeout(3.0)
try:
    banner = channel.recv(4096)
    print(f"Banner ({len(banner)} bytes): {banner!r}")
except Exception as e:
    print(f"No banner: {e}")

# Try sending some UDW command variants and reading responses
test_commands = [
    b'WebSocket PUB_WebSocketState 1\r\n',
    b'WebSocket PUB_WebSocketState 1\n',
    b'runUw mainApp "WebSocket PUB_WebSocketState 1"\r\n',
    b'WebSocket PUB_WebSocketState 1\r\n\x00',
]

for raw_cmd in test_commands:
    print(f"\n--- Sending: {raw_cmd!r} ---")
    try:
        channel.send(raw_cmd)
        time.sleep(2.0)
        resp = b""
        channel.settimeout(2.0)
        while True:
            try:
                chunk = channel.recv(4096)
                if not chunk:
                    break
                resp += chunk
            except Exception:
                break
        print(f"Response ({len(resp)} bytes): {resp!r}")
        if resp:
            print("Decoded:", resp.decode(errors="replace"))
            break   # got something — stop testing variants
    except Exception as e:
        print(f"Error: {e}")
        # Reopen channel if closed
        try:
            channel = transport.open_channel("direct-tcpip",
                                             dest_addr=("127.0.0.1", UDW_PORT),
                                             src_addr=("127.0.0.1", 0))
        except Exception:
            pass

channel.close()
ssh.close()
