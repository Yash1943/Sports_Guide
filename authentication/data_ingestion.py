import requests
from authentication.models import Player, PlayerStats

def fetch_and_store_players():
    api_url = f"https://cricapi.com/api/playerFinder?apikey={API_KEY}&name=virat"  # Replace with actual API
    response = requests.get(api_url)

    if response.status_code == 200:
        players = response.json()
        for player_data in players:
            player, created = Player.objects.get_or_create(
                name=player_data["name"],
                role=player_data["role"],
                team=player_data["team"]
            )

            # Store player stats
            PlayerStats.objects.update_or_create(
                player=player,
                defaults={
                    "batting_average": player_data["bat_avg"],
                    "strike_rate": player_data["strike_rate"],
                    "total_runs": player_data["runs"],
                    "wickets": player_data["wickets"],
                    "bowling_average": player_data["bowl_avg"],
                    "economy": player_data["economy"],
                    "recent_form": player_data["recent_form"],
                    "fitness_level": player_data["fitness"],
                    "match_experience": player_data["matches"],
                }
            )

        print("Player data updated successfully!")
    else:
        print("Failed to fetch data")

# Call this function periodically using Celery or Django Cron Jobs

