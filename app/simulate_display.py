from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import os

# Define paths within the Docker container
default_csv1 = "/app/data/robotics_competitions_data.csv"
default_csv2 = "/app/data/romanian_football_data.csv"
scraper_py_path = "/app/scraper.py"
scraper_robotica_py_path = "/app/scraper_robotica.py"
main_py_path = "/app/main.py"

app = Flask(__name__)

# Shared process state
process_status = {"status": "idle", "logs": ""}


def run_script(script_path, csv_path=None):
    """Run a script and capture its output."""
    global process_status
    command = ['python3', script_path]
    if csv_path:
        command.append(csv_path)

    try:
        process_status["status"] = "running"
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logs = []
        for line in process.stdout:
            logs.append(line.strip())
            process_status["logs"] = "\n".join(logs)
        for line in process.stderr:
            logs.append(f"ERROR: {line.strip()}")
            process_status["logs"] = "\n".join(logs)
        process.wait()
        if process.returncode == 0:
            logs.append(f"{os.path.basename(script_path)} executed successfully!")
        else:
            logs.append(f"{os.path.basename(script_path)} failed with return code {process.returncode}.")
        process_status["logs"] = "\n".join(logs)
    except Exception as e:
        logs.append(f"An error occurred: {str(e)}")
        process_status["logs"] = "\n".join(logs)
    finally:
        process_status["status"] = "idle"


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    """Handle script execution."""
    global process_status
    if process_status["status"] == "running":
        return jsonify({"status": "error", "message": "A process is already running!"})

    data = request.json
    selection = data.get("selection")

    if selection == "Get new football data":
        script_path = scraper_py_path
        csv_path = "/app/data/romanian_football_data.csv"
    elif selection == "Get new robotics data":
        script_path = scraper_robotica_py_path
        csv_path = "/app/data/robotics_competitions_data.csv"
    elif selection == "Robotics Default":
        script_path = main_py_path
        csv_path = default_csv1
    elif selection == "Football Default":
        script_path = main_py_path
        csv_path = default_csv2
    else:
        return jsonify({"status": "error", "message": "Invalid selection!"})

    threading.Thread(target=run_script, args=(script_path, csv_path)).start()
    return jsonify({"status": "success", "message": "Process started!"})


@app.route("/logs")
def logs():
    """Return the latest logs."""
    return jsonify({"status": process_status["status"], "logs": process_status["logs"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
