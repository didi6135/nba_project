import pytest

from repository.database import create_tables, get_db_connection, drop_all_tables
from repository.player_repository import insert_new_player, get_player_id_by_name, get_player_name_by_id


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


def test_insert_new_player(setup_database):
    player_id = insert_new_player('Michael Jordan')
    assert player_id is not None
    fetched_name = get_player_name_by_id(player_id)
    assert fetched_name == 'Michael Jordan'


def test_get_player_id_by_name(setup_database):
    player_id = insert_new_player('LeBron James')
    fetched_id = get_player_id_by_name('LeBron James')
    assert fetched_id == player_id


def test_get_player_name_by_id(setup_database):
    player_id = insert_new_player('Magic Johnson')
    fetched_name = get_player_name_by_id(player_id)
    assert fetched_name == 'Magic Johnson'


def test_insert_existing_player(setup_database):
    first_insert_id = insert_new_player('Kobe Bryant')
    second_insert_id = insert_new_player('Kobe Bryant')
    assert first_insert_id == second_insert_id


def test_get_nonexistent_player_by_name(setup_database):
    fetched_id = get_player_id_by_name('Non Existent Player')
    assert fetched_id is None


def test_get_nonexistent_player_by_id(setup_database):
    fetched_name = get_player_name_by_id(999999)
    assert fetched_name is None
