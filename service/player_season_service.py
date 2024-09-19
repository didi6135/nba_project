from repository.player_season_repository import get_player_by_position



# 1. function that get from the db all player base on the position
def filter_players_by_season(players, seasons):
    if not seasons:
        return players
    if len(seasons) == 1:
        return [player for player in players if player[3] == seasons[0]]
    return players


# 2. function that filter if the user send a season too

# 3. calc art
def calculate_atr(assists, turnovers):
    if turnovers == 0:
        return None
    return assists / turnovers

# 4. calc ppg
def calculate_ppg(points, games):
    if games == 0:
        return 0
    return points / games


def main_calc(position, seasons):
    player_by_position = get_player_by_position(position)

    filtered_players = filter_players_by_season(player_by_position, seasons)

    result = []
    for player in filtered_players:

        atr = calculate_atr(player['assists'], player['turnovers'])
        ppg = calculate_ppg(player['points'], player['games'])

        result.append({
            "playerName": player['player_name'],
            "team": player['team'],
            "season": player['season'],
            "points": player['points'],
            "games": player['games'],
            "twoPercent": player['two_percent'],
            "threePercent": player['three_percent'],
            "ATR": atr,
            "PPG": ppg
        })

    return result