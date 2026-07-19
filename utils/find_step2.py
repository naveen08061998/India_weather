import paramiko, time, requests, urllib3
urllib3.disable_warnings()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("15.77.36.76", port=22, username="root", password="myroot", timeout=30)

# Record dmesg line count before
stdin, stdout, _ = ssh.exec_command("dmesg | wc -l")
before = int(stdout.read().decode().strip() or "0")

# Run runUw via exec (not f-string)
cmd = '/core/bin/runUw mainApp "WebSocket PUB_getPingPongStatus 1"'
stdin, stdout, _ = ssh.exec_command(cmd)
stdout.read()
time.sleep(3)

# Check new dmesg lines
stdin, stdout, _ = ssh.exec_command("dmesg | tail -n +" + str(before + 1))
print("=== New dmesg lines ===")
print(stdout.read().decode(errors="replace").strip() or "(none)")

ssh.close()

# Probe CDM endpoints for tunnel/ping-pong status
BASE = "https://15.77.36.76"
for ep in [
    "/cdm/avnetwork/v1/configuration",
    "/cdm/avnetwork/v1/tunnels/1",
    "/cdm/stratus/v1/status",
    "/cdm/stratus/v1/tunnels",
    "/cdm/stratus/v1/tunnels/1/pingPong",
    "/cdm/iot/v1/status",
    "/cdm/iot/v1/tunnel",
    "/cdm/connectivity/v2/status",
]:
    try:
        r = requests.get(BASE + ep, verify=False, timeout=5)
        status = r.status_code
        body = r.text[:200] if r.ok else ""
        print(status, ep, body)
    except Exception as ex:
        print("ERR", ep, str(ex)[:60])

print("=== New mainApp log lines ===")
print(stdout.read().decode().strip() or "(none)")

stdin, stdout, _ = ssh2.exec_command("find /mnt/rw/.dune/machinedata/log/ -name *.log -exec grep -l PingPong {} ; 2>/dev/null")
print("\n=== Logs containing PingPong ===")
print(stdout.read().decode().strip() or "(none)")

ssh2.close()