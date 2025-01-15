import os
import random
import pandas as pd
from datetime import datetime, timedelta

# Define output directory
output_dir = "./scraper_data"
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Define league names and seasons
league_names = {
    "101": "RoboLeague Pro",
    "102": "RoboLeague Junior",
    "103": "RoboCup"
}
current_season = datetime.now().year
seasons = [f"{year}/{year + 1}" for year in range(current_season - 10, current_season)]


# Generate random team names
def generate_team_names(num_teams):
    prefixes = ["Cyber", "Mecha", "Robo", "Tech", "Neo"]
    suffixes = ["Warriors", "Titans", "Pioneers", "Blasters", "Innovators"]
    return [f"{random.choice(prefixes)} {random.choice(suffixes)}" for _ in range(num_teams)]


# Simulate matches
def simulate_matches(league_ids, seasons):
    data = []
    for league_id in league_ids:
        for season in seasons:
            teams = generate_team_names(10)  # Generate 10 teams per league
            for _ in range(20):  # Simulate 20 matches per season
                home_team = random.choice(teams)
                away_team = random.choice([team for team in teams if team != home_team])
                home_goals = random.randint(0, 5)
                away_goals = random.randint(0, 5)
                result = "HomeWin" if home_goals > away_goals else "AwayWin" if home_goals < away_goals else "Draw"

                match_date = datetime.now() - timedelta(
                    days=random.randint(0, 365 * 10))  # Random date in the last 10 years

                # Append match data
                data.append({
                    'Country': 'Robotica',
                    'League': league_names.get(league_id, 'Unknown'),
                    'Season': season,
                    'Date': match_date.strftime("%Y-%m-%d"),
                    'HomeTeam': home_team,
                    'AwayTeam': away_team,
                    'HomeGoals': home_goals,
                    'AwayGoals': away_goals,
                    'Result': result
                })
    return pd.DataFrame(data)


# Combine simulated data
def collect_robotics_data():
    league_ids = list(league_names.keys())
    simulated_data = simulate_matches(league_ids, seasons)
    output_file = os.path.join(output_dir, "robotics_competitions_data.csv")
    simulated_data.to_csv(output_file, index=False)
    print(f"Data collection complete. Saved to '{output_file}'")


# Execute the script
collect_robotics_data()
