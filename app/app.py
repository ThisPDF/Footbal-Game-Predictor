import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model
import rn_utils  # Custom utility module
import subprocess

app = Flask(__name__)

# Define paths
MODEL_PATH = "./model/"
DATA_FOLDER = "./app/data"
DATA_FOLDER_SCRAPED = "./scraper_data"
DEFAULT_CSVS = {
    "robotics": os.path.join(DATA_FOLDER, "robotics_competitions_data.csv"),
    "football": os.path.join(DATA_FOLDER, "romanian_football_data.csv"),
    "football_scraped": os.path.join(DATA_FOLDER_SCRAPED, "romanian_football_data.csv"),
    "robotics_scraped": os.path.join(DATA_FOLDER_SCRAPED, "robotics_competitions_data.csv")
}

# Global variables
data = None
current_csv_path = None
model = None
user_logs = []
last_trained_context = {"model_type": None}

# Ensure model directory exists
if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html", logs=user_logs)

@app.route("/select", methods=["POST"])
def select_data():
    """Handle data selection or scraper execution."""
    global current_csv_path, data

    selection = request.json.get("selection")
    if not selection:
        return jsonify({"status": "error", "message": "No selection made!"})

    try:
        if selection == "default1":
            current_csv_path = DEFAULT_CSVS["robotics"]
        elif selection == "default2":
            current_csv_path = DEFAULT_CSVS["football"]
        elif selection == "scraper1":
            subprocess.run(["python3", "./app/scraper_robotica.py"], check=True)
            current_csv_path = DEFAULT_CSVS["robotics_scraped"]
        elif selection == "scraper2":
            subprocess.run(["python3", "./app/scraper.py"], check=True)
            current_csv_path = DEFAULT_CSVS["football_scraped"]
        else:
            return jsonify({"status": "error", "message": "Invalid selection!"})

        print(f"Debug: Loading data from {current_csv_path}")
        data = pd.read_csv(current_csv_path)
        required_columns = ['HomeTeam', 'AwayTeam', 'Result', 'HomeGoals', 'AwayGoals', 'League']
        if not all(column in data.columns for column in required_columns):
            data = None
            return jsonify({"status": "error", "message": "Required data columns are missing."})

        user_logs.append(f"Data successfully loaded from: {os.path.basename(current_csv_path)}")
        return jsonify({"status": "success", "message": f"Data loaded from {current_csv_path}"})
    except Exception as e:
        print(f"Error loading data: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/get_teams", methods=["POST"])
def get_teams():
    """Retrieve teams based on the selected league."""
    global data

    if data is None:
        return jsonify({"status": "error", "message": "No data loaded!"})

    try:
        req_data = request.json
        league = req_data.get("league")

        if not league:
            return jsonify({"status": "error", "message": "No league provided!"})

        # Ensure the dataset contains the required columns
        required_columns = ["League", "HomeTeam"]
        for column in required_columns:
            if column not in data.columns:
                return jsonify({"status": "error", "message": f"Column '{column}' is missing from the dataset!"})

        # Filter teams by the selected league
        teams = data[data['League'] == league]['HomeTeam'].unique().tolist()
        print(f"Debug: Teams retrieved for league '{league}': {teams}")

        if not teams:
            return jsonify({"status": "error", "message": f"No teams found for league '{league}'."})

        return jsonify({"status": "success", "teams": sorted(teams)})
    except Exception as e:
        print(f"Error retrieving teams: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/train", methods=["POST"])
def train_model():
    """Train the model and save its context."""
    global data, model, current_csv_path, last_trained_context

    if not current_csv_path or data is None:
        user_logs.append("Error: No data selected for training.")
        return jsonify({"status": "error", "message": "No data selected!"})

    try:
        X, y = rn_utils.prepare_training_data(data)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=42)

        # Train the model
        print("Training model...")
        hyperparameters = {
            "num_layers": [2, 3],
            "units": [32, 64],
            "activation": ["relu", "tanh"],
            "learning_rate": [0.001, 0.0001],
            "epochs": [10, 20]
        }
        model, best_params = rn_utils.parallel_hyperparameter_tuning(
            hyperparameters, len(X[0]), X_train, X_val, y_train, y_val
        )

        # Save the model
        if "robotics" in current_csv_path:
            model_path = os.path.join(MODEL_PATH, "robotics_model.keras")
            last_trained_context["model_type"] = "robotics"
        elif "football" in current_csv_path:
            model_path = os.path.join(MODEL_PATH, "football_model.keras")
            last_trained_context["model_type"] = "football"

        model.save(model_path)
        user_logs.append(f"Model trained and saved at {model_path}. Best Hyperparameters: {best_params}")
        print(f"Debug: Model saved and last_trained_context updated to {last_trained_context}")
        return redirect(url_for("predictions"))  # Redirect to predictions page
    except Exception as e:
        print(f"Training error: {e}")
        user_logs.append(f"Error during training: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/predict", methods=["POST"])
def predict():
    """Make predictions using the trained model."""
    global model

    if not model:
        user_logs.append("Error: Model is not trained.")
        return jsonify({"status": "error", "message": "Model not trained!"})

    req_data = request.json
    home_team = req_data.get("home_team")
    away_team = req_data.get("away_team")

    if not home_team or not away_team:
        user_logs.append("Error: Teams not provided for prediction.")
        return jsonify({"status": "error", "message": "Teams not provided!"})

    try:
        # Use the model to predict
        prediction = rn_utils.predict_match(home_team, away_team, data, model)

        # Convert predictions to a JSON-serializable format
        prediction_cleaned = {key: float(value) for key, value in prediction.items()}
        user_logs.append(f"Prediction made for {home_team} vs {away_team}.")
        return jsonify({"status": "success", "prediction": prediction_cleaned})
    except Exception as e:
        print(f"Prediction error: {e}")
        user_logs.append(f"Error during prediction: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/predictions")
def predictions():
    """Render the predictions page."""
    global data
    if data is None:
        user_logs.append("Error: No data loaded for predictions.")
        return redirect(url_for("index"))
    leagues = sorted(data['League'].unique()) if data is not None else []
    return render_template("predictions.html", leagues=leagues, logs=user_logs)

if __name__ == "__main__":
    app.run(debug=True)
