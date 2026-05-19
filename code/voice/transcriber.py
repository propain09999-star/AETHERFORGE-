import sys, subprocess, time, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from code.grit.models import _groq_call

HOME         = Path.home()
WHISPER_BIN  = HOME / "whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL= HOME / "whisper.cpp/models/ggml-tiny.en.bin"

def transcribe_file(audio_file: str) -> str:
    if not WHISPER_BIN.exists():
        return "[whisper-cli not found — build whisper.cpp first]"
    if not WHISPER_MODEL.exists():
        return "[model not found — download ggml-tiny.en.bin]"
    try:
        r = subprocess.run(
            [str(WHISPER_BIN), "-m", str(WHISPER_MODEL),
             "-f", audio_file, "--language", "en", "-otxt", "-q"],
            capture_output=True, text=True, timeout=45)
        txt = Path(audio_file + ".txt")
        if txt.exists():
            out = txt.read_text().strip()
            txt.unlink()
            return out
        return r.stdout.strip() or "[no output]"
    except Exception as e:
        return f"[ASR error: {e}]"

def correct(raw: str) -> str:
    if not raw or raw.startswith("["):
        return raw
    return _groq_call(
        f"Fix punctuation and remove filler words only. Output corrected text only.\nRaw: {raw}",
        "llama-3.1-8b-instant"
    )

def record(seconds: int = 8) -> Path | None:
    if not shutil.which("termux-microphone-record"):
        print("[no termux-microphone-record]")
        return None
    f = Path(f"/tmp/chunk_{int(time.time())}.wav")
    subprocess.run(["termux-microphone-record", "-f", str(f),
                    "-l", str(seconds), "start"], capture_output=True)
    time.sleep(seconds + 0.8)
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
    return f if f.exists() else None

class Transcriber:
    def __init__(self):
        print(f"✓ Transcriber online")
        print(f"  whisper: {'✓' if WHISPER_BIN.exists() else '✗ not built'}")
        print(f"  model:   {'✓' if WHISPER_MODEL.exists() else '✗ not downloaded'}")

    def live(self, seconds: int = 8):
        print(f"🎤 Live mode ({seconds}s chunks) | Ctrl+C to stop")
        while True:
            f = record(seconds)
            if f:
                raw = transcribe_file(str(f))
                print(f"📝 {correct(raw)}")
                f.unlink(missing_ok=True)
            time.sleep(0.3)

    def file(self, path: str) -> str:
        raw = transcribe_file(path)
        return correct(raw)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--live",  action="store_true")
    p.add_argument("--file",  type=str)
    p.add_argument("--check", action="store_true")
    p.add_argument("--seconds", type=int, default=8)
    args = p.parse_args()
    t = Transcriber()
    if args.check:
        pass
    elif args.file:
        print(t.file(args.file))
    elif args.live:
        t.live(args.seconds)

