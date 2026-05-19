import json
import shutil
import subprocess
import time


def _run(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return None


def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except Exception:
        return None


def get_loadavg():
    try:
        with open("/proc/loadavg", "r") as f:
            parts = f.read().split()
            return {"1m": float(parts[0]), "5m": float(parts[1]), "15m": float(parts[2])}
    except Exception:
        return None


def get_memory():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                k, v = line.split(":", 1)
                meminfo[k.strip()] = v.strip()

        total_kb = int(meminfo["MemTotal"].split()[0])
        avail_kb = int(meminfo["MemAvailable"].split()[0])
        used_kb = total_kb - avail_kb

        return {
            "total_mb": round(total_kb / 1024, 2),
            "available_mb": round(avail_kb / 1024, 2),
            "used_mb": round(used_kb / 1024, 2),
            "used_pct": round((used_kb / total_kb) * 100, 2)
        }
    except Exception:
        return None


def get_storage(path="/data/data/com.termux/files/home"):
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)

        return {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "used_pct": round((used_gb / total_gb) * 100, 2)
        }
    except Exception:
        return None


def get_battery():
    raw = _run(["termux-battery-status"])
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return {
            "percentage": data.get("percentage"),
            "status": data.get("status"),
            "plugged": data.get("plugged"),
            "temperature": data.get("temperature"),
            "health": data.get("health"),
        }
    except Exception:
        return None


def snapshot():
    return {
        "uptime_seconds": get_uptime(),
        "loadavg": get_loadavg(),
        "memory": get_memory(),
        "storage": get_storage(),
        "battery": get_battery(),
        "timestamp": time.time()
    }

