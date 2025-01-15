import os
from datetime import datetime
import requests
import pandas as pd
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

# API-Football credentials
API_KEY = "772c32def89c5f1f65dd7cc1c04682ef"  # Replace with your actual API key
API_HOST = "https://v3.football.api-sports.io/"
league_ids = ["555", "283", "285", "284"]
current_season = datetime.now().year
seasons = [f"{year}/{year + 1}" for year in range(current_season - 10, current_season)]
football_data_co_uk_url = "https://www.football-data.co.uk/new/ROU.csv"

# Directory for saving data
output_dir = "scraper_data"
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# League name mapping
league_names = {
    "555": "SuperCupa",
    "283": "Liga I",
    "285": "Cupa României",
    "284": "Liga II"
}

# Function to remove diacritics from text
def remove_diacritics(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

# Fetch data from API-Football for a single league and season
def fetch_league_season_data(league_id, season):
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "v3.football.api-sports.io"}
    querystring = {"league": league_id, "season": season.split("/")[0]}
    url = f"{API_HOST}fixtures"

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            api_data = []
            for match in response.json().get('response', []):
                try:
                    home_team = remove_diacritics(match['teams']['home']['name'])
                    away_team = remove_diacritics(match['teams']['away']['name'])
                    home_goals = match['goals']['home']
                    away_goals = match['goals']['away']
                    result = "HomeWin" if home_goals > away_goals else "AwayWin" if home_goals < away_goals else "Draw"

                    # Append match data
                    api_data.append({
                        'Country': 'Romania',
                        'League': league_names.get(league_id, 'Unknown'),
                        'Season': season,
                        'Date': match['fixture']['date'],
                        'HomeTeam': home_team,
                        'AwayTeam': away_team,
                        'HomeGoals': home_goals,
                        'AwayGoals': away_goals,
                        'Result': result
                    })
                except Exception as e:
                    print("Error processing match:", e)
            return api_data
        else:
            print(f"API request failed for league {league_id}, season {season} with status:", response.status_code)
            return []
    except Exception as e:
        print(f"Error fetching data for league {league_id}, season {season}: {e}")
        return []

# Fetch data from Football-Data.co.uk
def fetch_football_data_co_uk():
    print("Fetching data from Football-Data.co.uk")
    try:
        co_uk_data = pd.read_csv(football_data_co_uk_url)
        # Normalize column names and data formats
        co_uk_data['HomeTeam'] = co_uk_data['Home'].apply(remove_diacritics)
        co_uk_data['AwayTeam'] = co_uk_data['Away'].apply(remove_diacritics)
        co_uk_data = co_uk_data.rename(columns={
            'HG': 'HomeGoals',
            'AG': 'AwayGoals',
            'Res': 'Result'
        })
        co_uk_data['Result'] = co_uk_data['Result'].map(
            lambda x: 'HomeWin' if x == 'H' else 'AwayWin' if x == 'A' else 'Draw')
        co_uk_data['Country'] = 'Romania'  # Add the country column
        return co_uk_data[
            ['Country', 'League', 'Season', 'Date', 'HomeTeam', 'AwayTeam', 'HomeGoals', 'AwayGoals', 'Result']]
    except Exception as e:
        print(f"Failed to fetch or parse data from Football-Data.co.uk: {e}")
        return pd.DataFrame()

# Collect data from API-Football using multithreading
def fetch_api_football_data(league_ids, seasons):
    api_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_league_season = {
            executor.submit(fetch_league_season_data, league_id, season): (league_id, season)
            for league_id in league_ids for season in seasons
        }
        for future in as_completed(future_to_league_season):
            league_id, season = future_to_league_season[future]
            try:
                data = future.result()
                api_data.extend(data)
            except Exception as e:
                print(f"Error fetching data for league {league_id}, season {season}: {e}")
    return pd.DataFrame(api_data)

# Collect data from multiple sources
def collect_combined_data():
    # Fetch data from API-Football
    print("Fetching data from API-Football")
    api_data = fetch_api_football_data(league_ids, seasons)

    # Fetch data from Football-Data.co.uk
    co_uk_data = fetch_football_data_co_uk()

    # Combine datasets
    combined_data = pd.concat([api_data, co_uk_data], ignore_index=True)
    output_file = os.path.join(output_dir, "romanian_football_data.csv")
    combined_data.to_csv(output_file, index=False)
    print(f"Data collection complete. Saved to '{output_file}'")

# Execute data collection
collect_combined_data()
