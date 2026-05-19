from code.api.server import run_server


def banner():
    print("╔══════════════════════════════════════════════════════╗")
    print("║     AETHORFORGE v2 — Modern Tailwind HUD Stack       ║")
    print("║   Flask · Telemetry · Router · HUD · Termux Ready    ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    banner()
    run_server(host="127.0.0.1", port=8080)
