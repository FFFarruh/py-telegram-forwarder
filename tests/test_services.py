import psycopg
from services import delete_subscribtions, insert_db
from settings import Settings
import pytest

setting = Settings()


@pytest.fixture
async def delete_table():
    with psycopg.connect(setting.db_url) as connect:
        with connect.cursor() as cur:
            cur.execute("DELETE FROM db_subscribtions")


@pytest.mark.asyncio
async def test_insert_and_delete_subsсribtion(delete_table):
    with psycopg.connect(setting.db_url) as connect:

        with connect.cursor() as cur:

            await insert_db(connect, ("123", "321"))
            cur.execute("SELECT user_id, chat_id FROM db_subscribtions")

            assert cur.fetchone() == ("123", "321")

            await delete_subscribtions(connect, ("123", "321"))

            assert await is_empty_table(cur) == (0,)


async def is_empty_table(cur):
    cur.execute("SELECT COUNT(*) FROM db_subscribtions")
    return cur.fetchone()
