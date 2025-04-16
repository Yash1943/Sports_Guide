import requests
from authentication.models import Player_reco, PlayerStats

def fetch_and_store_players():
    api_url = "https://example.com/cricket-players-api"  # Replace with real API
    response = requests.get(api_url)

    if response.status_code == 200:
        players = response.json()
        for player_data in players:
            player, created = Player_reco.objects.get_or_create(
                name=player_data["name"],
                defaults={"role": player_data["role"], "team": player_data.get("team", "")}
            )

            PlayerStats.objects.update_or_create(
                player=player,
                defaults={
                    "batting_average": player_data["bat_avg"],
                    "strike_rate": player_data["strike_rate"],
                    "total_runs": player_data["runs"],
                    "wickets": player_data["wickets"],
                    "bowling_average": player_data["bowl_avg"],
                    "economy": player_data["economy"],
                }
            )
    else:
        print("Failed to fetch data")
