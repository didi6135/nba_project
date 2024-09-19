import pytest

from repository.database import create_tables, get_db_connection, drop_all_tables
from repository.player_repository import insert_new_player


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


def test_insert_player(setup_database):
    player_id = insert_new_player('david')
    assert player_id is not None

def test_insert_existing_player(setup_database):
    first_insert_id = insert_new_player('david')

    second_insert_id = insert_new_player('david')
    assert first_insert_id == second_insert_id