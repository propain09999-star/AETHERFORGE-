python - << 'PY'
import os
from pathlib import Path

BASE = Path(".").resolve()

def write_file(path: str, content: str):
    p = BASE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def touch(path: str):
    p = BASE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")

print("[+] Building AETHORFORGE Modern Tailwind HUD Repo...")

# ---------------------------
# Core Repo Files
# ---------------------------
write_file(".gitignore", """__pycache__/
*.pyc
*.log
data/*.db
.env
""")

write_file("requirements.txt", """flask
requests
""")

write_file("README.md", """# AETHORFORGE (Modern Tailwind HUD)

A mobile-first hybrid routing telemetry HUD.

## Install (Termux)
```bash
pkg update -y
pkg install python git -y
pip install -r requirements.txt
