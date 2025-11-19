from flask import Flask, request, jsonify
from system_control import SystemController

app = Flask(__name__)
controller = SystemController()

@app.route("/start", methods=["POST"])
def start():
    controller.start_system()
    return jsonify({"status": "running", "message": "Gesture system started."})

@app.route("/stop", methods=["POST"])
def stop():
    controller.stop_system()
    return jsonify({"status": "stopped", "message": "Gesture system stopped."})

@app.route("/recalibrate", methods=["POST"])
def recalibrate():
    msg = controller.recalibrate()
    return jsonify({"status": "ok", "message": msg})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": controller.status})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
