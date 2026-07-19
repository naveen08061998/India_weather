"""Kill deadlocked mainApp (PID 1701) + hanging runUw processes; launchsingle.sh restarts it."""
import time
import paramiko
from utils.config import cfg

def new_ssh():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(cfg.DEVICE_HOST, port=cfg.DEVICE_SFTP_PORT,
              username=cfg.DEVICE_SFTP_USER, password=cfg.DEVICE_SFTP_PASSWORD, timeout=10)
    return c

def shell(ssh, cmd, timeout=10):
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    try:
        out = o.read().decode(errors="replace").strip()
        return out
    except Exception:
        return ""

def run_udw(ssh, cmd, timeout=12):
    try:
        _, o, _ = ssh.exec_command(f'/core/bin/runUw mainApp "{cmd}"', timeout=timeout)
        return o.read().decode(errors="replace").strip()
    except Exception:
        return ""

print("=== Step 1: Kill hanging runUw processes ===")
ssh = new_ssh()
hung_pids = shell(ssh, "pgrep -f 'runUw mainApp'")
print(f"Hanging runUw PIDs: {hung_pids!r}")
if hung_pids:
    shell(ssh, f"kill -9 {hung_pids.replace(chr(10), ' ')}")
    print("Killed.")
ssh.close()
time.sleep(2)

print("\n=== Step 2: Kill mainApp (PID 1701 / pgrep) — launchsingle.sh will restart it ===")
ssh = new_ssh()
mainapp_pid = shell(ssh, "pgrep -f './mainApp$'")
if not mainapp_pid:
    mainapp_pid = shell(ssh, "pgrep -f '/mainApp'")
print(f"mainApp PIDs: {mainapp_pid!r}")
if mainapp_pid:
    shell(ssh, f"kill -9 {mainapp_pid.replace(chr(10), ' ')}")
    print("Killed mainApp. launchsingle.sh should restart it...")
else:
    print("mainApp not found via pgrep -f — trying kill by known PID 1701")
    shell(ssh, "kill -9 1701")
ssh.close()

print("\nWaiting 40s for mainApp to restart and initialise...")
time.sleep(40)

print("\n=== Step 3: Verify recovery ===")
for attempt in range(8):
    ssh = new_ssh()
    pid = shell(ssh, "pgrep -f mainApp | head -1")
    r1 = run_udw(ssh, "WebSocket PUB_WebSocketState 1", timeout=12)
    r2 = run_udw(ssh, "WebSocket PUB_WebSocketState 2", timeout=12)
    ssh.close()
    print(f"  [{attempt+1}] mainApp_pid={pid!r}  T1={r1!r}  T2={r2!r}")
    if r1 and r2:
        print("\nmainApp is responding — WebSocket service recovered!")
        break
    time.sleep(10)
else:
    print("\nWARNING: WebSocket still not responding. Device may need a reboot.")

print("Done.")
