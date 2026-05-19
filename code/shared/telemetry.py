import subprocess, time
from pathlib import Path

def get_telemetry() -> dict:
    """Real device stats from /proc — works on Termux"""
    # RAM
    try:
        lines = open("/proc/meminfo").readlines()
        total = int(lines[0].split()[1]) // 1024
        avail = int(lines[2].split()[1]) // 1024
        used  = total - avail
    except:
        total = used = avail = 0

    # CPU load — parse from uptime output (loadavg not accessible in Termux)
    try:
        r = subprocess.run(["uptime"], capture_output=True, text=True)
        # uptime output contains "load average: 1.23, 1.45, 1.67"
        if "load average:" in r.stdout:
            load = r.stdout.split("load average:")[-1].strip().split(",")[0].strip()
        else:
            load = "n/a"
    except:
        load = "n/a"

    # Storage
    try:
        r = subprocess.run(["df", "-h", str(Path.home())],
            capture_output=True, text=True)
        storage = r.stdout.split("\n")[1].split()[3] + " free"
    except:
        storage = "?"

    # Uptime
    try:
        r = subprocess.run(["uptime"], capture_output=True, text=True)
        raw = r.stdout.strip()
        if "up" in raw:
            uptime = raw.split("up")[1].split(",")[0].strip()
        else:
            uptime = raw
    except:
        uptime = "n/a"

    return {
        "ram_used_mb":  used,
        "ram_total_mb": total,
        "ram_free_mb":  avail,
        "cpu_load":     load,
        "storage":      storage,
        "uptime":       uptime,
        "timestamp":    time.strftime("%H:%M:%S"),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_telemetry(), indent=2))

