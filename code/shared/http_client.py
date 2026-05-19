import subprocess, json, os

def http_post(url: str, payload: dict, headers: dict = None) -> dict:
    """curl-based HTTP client — works on Termux without requests library"""
    h = headers or {}
    header_args = []
    for k, v in h.items():
        header_args += ["-H", f"{k}: {v}"]
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Content-Type: application/json",
             *header_args,
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def http_get(url: str, headers: dict = None) -> dict:
    h = headers or {}
    header_args = []
    for k, v in h.items():
        header_args += ["-H", f"{k}: {v}"]
    try:
        result = subprocess.run(
            ["curl", "-s", url, *header_args],
            capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

