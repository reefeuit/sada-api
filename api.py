from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os

app = Flask(__name__)

latest_reading = None


def authorized():
    key = os.environ.get("SADA_API_KEY", "")
    supplied = request.headers.get("X-API-Key", "")
    return bool(key) and supplied == key


@app.get("/")
def home():
    return jsonify({"status": "SADA API online"})


@app.get("/latest")
def latest():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    if latest_reading is None:
        return jsonify({
            "value": None,
            "time": None,
            "status": "waiting"
        })

    return jsonify(latest_reading)


@app.post("/api/sensor")
def receive_sensor():
    global latest_reading

    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    value = data.get("value")

    try:
        value = float(value)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid value"}), 400

    latest_reading = {
        "value": value,
        "time": datetime.now(timezone.utc).isoformat()
    }

    return jsonify({"ok": True, "received": latest_reading})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
