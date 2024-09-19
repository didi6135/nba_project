import requests
from toolz import pipe, concat

# Assuming you have PlayerSeason and repository functions ready
from models.playerSeason import PlayerSeason
from repository.player_repository import insert_new_player
from repository.player_season_repository import insert_player_season


def create_player_season(player_data, player_id):
    return PlayerSeason(
        player_id=player_id,
        season=player_data.get("season", ""),
        team=player_data.get("team", ""),
        points=player_data.get("points", 0),
        games=player_data.get("games", 0),
        twoPercent=player_data.get("twoPercent", 0.0),
        threePercent=player_data.get("threePercent", 0.0),
        ATR=player_data.get("ATR", 0.0),
        PPG_ratio=player_data.get("PPG_ratio", 0.0)
    )


def fetch_players_by_season(season):
    nba_url = f'http://b8c40s8.143.198.70.30.sslip.io/api/PlayerDataTotals/query?season={season}&pageSize=10'
    try:
        response = requests.get(nba_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        return []



def create_and_insert_player(player_name):
    return insert_new_player(player_name)


def process_player(player):
    new_player_id = create_and_insert_player(player['playerName'])
    player_season = create_player_season(player, new_player_id)
    insert_player_season(player_season)


def get_players_for_all_seasons():
    all_seasons = [2022, 2023, 2024]
    return pipe(
        all_seasons,
        lambda seasons: map(fetch_players_by_season, seasons),
        concat,
        lambda players: map(lambda player: process_player(player), players),
        list
    )


print(get_players_for_all_seasons())
