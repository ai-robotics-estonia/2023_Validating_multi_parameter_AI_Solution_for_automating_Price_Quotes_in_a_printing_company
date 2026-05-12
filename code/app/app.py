"""Minimal Flask UI that polls a long-running background pipeline.

This is a generic progress-tracker skeleton. The actual pipeline that the
``/start_process`` endpoint launches is intentionally not included here —
plug in your own generator that yields ``(step_number, message)`` tuples.
"""
import threading
from flask import Flask, render_template, jsonify

app = Flask(__name__)

progress_data = {
    "step": 0,
    "status": "Not started",
    "result": None,
    "final_result": None,
}
process_thread: threading.Thread | None = None


def step_label(step: int) -> str:
    labels = {
        1: "Step 1 result: ",
        2: "Step 2 result: ",
        3: "Step 3 result: ",
        4: "Step 4 result: ",
        5: "Step 5 result: ",
    }
    return labels.get(step, "Unknown step")


def run_pipeline():
    """Replace this with your own pipeline. It must yield (step, message)."""
    for i in range(1, 6):
        progress_data["step"] = i
        progress_data["status"] = f"Step {i} in progress..."
        progress_data["result"] = step_label(i) + "(placeholder)"
        progress_data["status"] = f"Step {i} completed"
    progress_data["status"] = "Completed"
    progress_data["final_result"] = "Final answer: SUCCESS"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_process", methods=["POST"])
def start_process():
    global process_thread
    if process_thread is None or not process_thread.is_alive():
        process_thread = threading.Thread(target=run_pipeline)
        process_thread.start()
    return jsonify({"message": "Process started!"}), 202


@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress_data), 200


@app.route("/reset", methods=["POST"])
def reset_process():
    global progress_data, process_thread
    if process_thread and process_thread.is_alive():
        process_thread = None
    progress_data = {
        "step": 0,
        "status": "Not started",
        "result": None,
        "final_result": None,
    }
    return jsonify({"message": "Process reset!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
