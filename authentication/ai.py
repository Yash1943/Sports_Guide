import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from authentication.models import Player, PlayerStats

# Train AI Model for player recommendation
def train_model():
    data = []
    players = PlayerStats.objects.all()

    if not players.exists():
        print("No player stats found in database")
        return None

    for player_stat in players:
        data.append([
            player_stat.player.name,
            player_stat.batting_average,
            player_stat.strike_rate,
            player_stat.total_runs,
            player_stat.wickets,
            player_stat.bowling_average,
            player_stat.economy,
            player_stat.recent_form,
            player_stat.fitness_level,
            player_stat.match_experience
        ])

    if not data:
        print("No valid player data found")
        return None

    print(f"Training model with {len(data)} players")  # Debug print
    
    df = pd.DataFrame(data, columns=["name", "bat_avg", "strike_rate", "runs", "wickets", 
                                   "bowl_avg", "economy", "recent_form", "fitness", "matches"])

    X = df[["bat_avg", "strike_rate", "runs", "wickets", "bowl_avg", "economy", "recent_form", "fitness", "matches"]]
    y = df["name"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    print("Model training completed")  # Debug print
    return model

# Predict Winning Probability
def predict_winning_probability(team1, team2):
    team1_stats = PlayerStats.objects.filter(player__team=team1)
    team2_stats = PlayerStats.objects.filter(player__team=team2)

    if not team1_stats.exists() or not team2_stats.exists():
        return {"error": "Insufficient data to predict"}

    team1_strength = np.mean([p.batting_average + p.bowling_average + p.fitness_level for p in team1_stats])
    team2_strength = np.mean([p.batting_average + p.bowling_average + p.fitness_level for p in team2_stats])

    total_strength = team1_strength + team2_strength
    team1_prob = (team1_strength / total_strength) * 100
    team2_prob = (team2_strength / total_strength) * 100

    return {
        team1: f"{team1_prob:.2f}%",
        team2: f"{team2_prob:.2f}%"
    }
