import pytest
from models.playerSeason import PlayerSeason
from repository.database import create_tables, get_db_connection, drop_all_tables
from repository.player_season_repository import insert_player_season, get_player_by_position


@pytest.fixture(scope='module')
def setup_database():
    create_tables()
    yield
    conn = get_db_connection()
    cur = conn.cursor()
    drop_all_tables()
    conn.commit()
    cur.close()
    conn.close()


def test_insert_player_season(setup_database):
    player_season = PlayerSeason(
        player_id=1,
        position="PG",
        season=2024,
        team="LAL",
        points=1000,
        games=80,
        twoPercent=0.5,
        threePercent=0.35,
        ATR=2.0,
        PPG_ratio=25.0,
        assists=200,
        turnovers=100
    )

    new_id = insert_player_season(player_season)
    assert new_id is not None


def test_insert_existing_player_season(setup_database):
    player_season = PlayerSeason(
        player_id=1,
        position="PG",
        season=2024,
        team="LAL",
        points=1000,
        games=80,
        twoPercent=0.5,
        threePercent=0.35,
        ATR=2.0,
        PPG_ratio=25.0,
        assists=200,
        turnovers=100
    )

    first_insert_id = insert_player_season(player_season)
    second_insert_id = insert_player_season(player_season)
    assert first_insert_id == second_insert_id


def test_get_player_by_position(setup_database):
    player_season = PlayerSeason(
        player_id=2,
        position="SG",
        season=2024,
        team="BOS",
        points=800,
        games=70,
        twoPercent=0.6,
        threePercent=0.4,
        ATR=1.5,
        PPG_ratio=20.0,
        assists=150,
        turnovers=75
    )

    insert_player_season(player_season)

    players = get_player_by_position("SG")
    assert len(players) > 0
    assert players[0][1] == 'SG'


def test_get_nonexistent_position(setup_database):
    players = get_player_by_position("C")
    assert len(players) == 0
