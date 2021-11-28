import psycopg
import pytest
from repositories import delete_subscribtions, insert_db
from settings import Settings

setting = Settings()


@pytest.fixture
async def delete_table():
    with psycopg.connect(setting.db_test_url) as connect:
        with connect.cursor() as cur:
            cur.execute("DELETE FROM db_subscribtions")


@pytest.fixture
async def url():
    return setting.db_test_url


@pytest.mark.asyncio
async def test_insert_and_delete_subsсribtion(delete_table, url):
    with psycopg.connect(url) as connect:

        with connect.cursor() as cur:

            await insert_db(url, ("123", "321"))
            cur.execute("SELECT user_id, chat_id FROM db_subscribtions")

            assert cur.fetchone() == ("123", "321")

            await delete_subscribtions(url, ("123", "321"))

            assert await is_empty_table(cur) == (0,)


async def is_empty_table(cur):
    cur.execute("SELECT COUNT(*) FROM db_subscribtions")
    return cur.fetchone()
