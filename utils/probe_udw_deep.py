"""
Deep probe: get all listening ports on device, try UDW binary framing on 6130,
and check if mainApp exposes a shell/telnet on any port.
"""
import sys, os, time, struct, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import paramiko
from utils.config import cfg

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(cfg.DEVICE_HOST, port=cfg.DEVICE_SFTP_PORT,
            username=cfg.DEVICE_SFTP_USER, password=cfg.DEVICE_SFTP_PASSWORD, timeout=15)

def run(cmd, timeout=10):
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    return o.read().decode(errors="replace").strip()

# 1. Full port listing
print("=== All LISTEN ports ===")
print(run("netstat -tlnp 2>/dev/null | grep LISTEN"))

# 2. Check for a dune/stratus debug shell or socket
print("\n=== Stratus/Dune debug sockets ===")
print(run("find /tmp /var/run /dev -name '*.sock' -o -name '*debug*' -o -name '*udw*' 2>/dev/null | head -20"))

# 3. Check the /proc/net/tcp for ALL ports (hex)
print("\n=== /proc/net/tcp (local addr:port) ===")
raw = run("cat /proc/net/tcp")
for line in raw.splitlines()[1:]:  # skip header
    parts = line.split()
    if len(parts) >= 4 and parts[3] == "0A":  # 0A = LISTEN
        local = parts[1]
        ip_hex, port_hex = local.split(":")
        ip = ".".join(str(int(ip_hex[i:i+2], 16)) for i in (6, 4, 2, 0))
        port = int(port_hex, 16)
        print(f"  LISTEN {ip}:{port}")

# 4. Look for any runUw / uw binary anywhere on the device
print("\n=== Searching for runUw/uwcli binary ===")
print(run("find / -xdev -name 'runUw' -o -name 'runuw' -o -name 'uwcli' -o -name 'uw' 2>/dev/null | head -10"))

# 5. Try connecting to port 6130 from the device itself and send a few binary frames
print("\n=== Testing UDW port 6130 with various framing ===")
transport = ssh.get_transport()

def try_udw(payload: bytes, label: str):
    try:
        ch = transport.open_channel("direct-tcpip",
                                    dest_addr=("127.0.0.1", 6130),
                                    src_addr=("127.0.0.1", 0))
        ch.settimeout(3.0)
        ch.send(payload)
        time.sleep(2.0)
        resp = b""
        try:
            while True:
                chunk = ch.recv(4096)
                if not chunk: break
                resp += chunk
        except Exception:
            pass
        ch.close()
        print(f"  [{label}] sent={len(payload)}B resp={len(resp)}B {resp[:80]!r}")
    except Exception as ex:
        print(f"  [{label}] ERROR: {ex}")

cmd = "WebSocket PUB_WebSocketState 1"
# length-prefixed variants
try_udw(struct.pack(">I", len(cmd)) + cmd.encode(), "4-byte big-endian length prefix")
try_udw(struct.pack("<I", len(cmd)) + cmd.encode(), "4-byte little-endian length prefix")
try_udw(struct.pack(">H", len(cmd)) + cmd.encode(), "2-byte big-endian length prefix")
# null-terminated
try_udw(cmd.encode() + b"\x00", "null-terminated")
# JSON wrapped
j = json.dumps({"cmd": cmd}).encode()
try_udw(j + b"\n", "JSON newline")
try_udw(j + b"\x00", "JSON null-term")

# 6. Try executing via SSH shell (interactive channel)
print("\n=== Interactive SSH shell test ===")
chan = ssh.invoke_shell()
chan.settimeout(3.0)
time.sleep(1.0)
try:
    banner = chan.recv(4096).decode(errors="replace")
    print("Shell banner:", repr(banner[:200]))
except Exception:
    pass
chan.send(f'runUw mainApp "{cmd}"\n'.encode())
time.sleep(2.0)
try:
    out = chan.recv(4096).decode(errors="replace")
    print("Shell output:", repr(out[:400]))
except Exception as e:
    print("No output:", e)
chan.close()

ssh.close()
