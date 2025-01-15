import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from multiprocessing import Pool, Manager
import itertools

def aggregate_team_data(team, data):
    """Aggregate historical data for a given team."""
    team_home_games = data[data['HomeTeam'] == team]
    team_away_games = data[data['AwayTeam'] == team]

    total_games = len(team_home_games) + len(team_away_games)
    if total_games == 0:
        return np.zeros(6)  # Return zeros if no games found

    home_goals_scored = team_home_games['HomeGoals'].sum()
    away_goals_scored = team_away_games['AwayGoals'].sum()
    home_goals_conceded = team_home_games['AwayGoals'].sum()
    away_goals_conceded = team_away_games['HomeGoals'].sum()

    total_goals_scored = home_goals_scored + away_goals_scored
    total_goals_conceded = home_goals_conceded + away_goals_conceded

    home_wins = len(team_home_games[team_home_games['Result'] == 'HomeWin'])
    away_wins = len(team_away_games[team_away_games['Result'] == 'AwayWin'])
    draws = len(team_home_games[team_home_games['Result'] == 'Draw']) + len(
        team_away_games[team_away_games['Result'] == 'Draw'])

    win_rate = (home_wins + away_wins) / total_games
    draw_rate = draws / total_games
    loss_rate = 1 - win_rate - draw_rate

    return np.array([
        total_goals_scored / total_games,
        total_goals_conceded / total_games,
        win_rate,
        draw_rate,
        loss_rate,
        total_games
    ])

def build_model(input_shape, num_layers=3, units=64, activation='relu', learning_rate=0.001):
    """Build and compile a Keras model."""
    model = Sequential()
    model.add(Input(shape=(input_shape,)))
    for _ in range(num_layers):
        model.add(Dense(units, activation=activation))
    model.add(Dense(3, activation='softmax'))
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_and_evaluate_model(params):
    """Train and evaluate a model."""
    num_layers, units, activation, learning_rate, epochs, input_shape, X_train, X_val, y_train, y_val, return_dict = params

    model = build_model(input_shape, num_layers, units, activation, learning_rate)
    history = model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val), batch_size=32, verbose=0)

    val_accuracy = history.history['val_accuracy'][-1]
    return_dict[(num_layers, units, activation, learning_rate, epochs)] = (val_accuracy, model)

def parallel_hyperparameter_tuning(hyperparameters, input_shape, X_train, X_val, y_train, y_val):
    """Perform parallel hyperparameter tuning."""
    hyperparameter_combinations = list(itertools.product(
        hyperparameters['num_layers'],
        hyperparameters['units'],
        hyperparameters['activation'],
        hyperparameters['learning_rate'],
        hyperparameters['epochs']
    ))

    manager = Manager()
    return_dict = manager.dict()

    params = [
        (num_layers, units, activation, learning_rate, epochs, input_shape, X_train, X_val, y_train, y_val, return_dict)
        for num_layers, units, activation, learning_rate, epochs in hyperparameter_combinations
    ]

    with Pool(processes=4) as pool:
        pool.map(train_and_evaluate_model, params)

    best_params = max(return_dict.keys(), key=lambda x: return_dict[x][0])
    best_val_accuracy, best_model = return_dict[best_params]

    return best_model, best_params

def predict_match(home_team, away_team, data, model):
    """Predict the outcome of a match between two teams."""
    home_team_data = aggregate_team_data(home_team, data)
    away_team_data = aggregate_team_data(away_team, data)

    match_input = np.concatenate((home_team_data, away_team_data)).reshape(1, -1)
    prediction = model.predict(match_input)

    return {
        "Home Win": prediction[0][0] * 100,
        "Draw": prediction[0][1] * 100,
        "Away Win": prediction[0][2] * 100
    }

def prepare_training_data(data):
    """Prepare features and labels for model training."""
    X = []
    y = []
    for _, row in data.iterrows():
        home_data = aggregate_team_data(row['HomeTeam'], data)
        away_data = aggregate_team_data(row['AwayTeam'], data)
        X.append(np.concatenate((home_data, away_data)))
        result_mapping = {'HomeWin': 0, 'Draw': 1, 'AwayWin': 2}
        y.append(result_mapping.get(row['Result'], -1))
    if -1 in y:
        raise ValueError("Invalid results in data.")
    return np.array(X), np.array(y)

