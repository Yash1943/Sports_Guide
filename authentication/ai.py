import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from authentication.models import Player, PlayerStats

# Train AI Model for player recommendation
def train_model():
    data = []
    players = PlayerStats.objects.all()

    for player in players:
        data.append([
            player.player.name,
            player.batting_average,
            player.strike_rate,
            player.total_runs,
            player.wickets,
            player.bowling_average,
            player.economy,
            player.recent_form,
            player.fitness_level,
            player.match_experience
        ])

    if not data:
        return None  # Avoid error if no players exist

    df = pd.DataFrame(data, columns=["name", "bat_avg", "strike_rate", "runs", "wickets", 
                                     "bowl_avg", "economy", "recent_form", "fitness", "matches"])

    X = df[["bat_avg", "strike_rate", "runs", "wickets", "bowl_avg", "economy", "recent_form", "fitness", "matches"]]
    y = df["name"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

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
