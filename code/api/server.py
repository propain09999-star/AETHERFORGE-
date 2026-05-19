from flask import Flask, jsonify, send_from_directory, request
from code.core.telemetry import TelemetryEngine

app = Flask(__name__)
telemetry = TelemetryEngine()


@app.route("/")
def home():
    return send_from_directory("ui", "index.html")


@app.route("/api/telemetry")
def api_telemetry():
    return jsonify(telemetry.generate())


@app.route("/api/query", methods=["POST"])
def api_query():
    payload = request.get_json(force=True)
    q = payload.get("query", "")
    telemetry.update_query(q)
    return jsonify({"ok": True, "query": q})


@app.route("/api/history")
def api_history():
    return jsonify({"history": telemetry.get_history()})


def run_server(host="127.0.0.1", port=8080):
    print(f"✓ [SERVER ONLINE] http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

