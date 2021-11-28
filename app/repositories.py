import psycopg


async def create_db(url):
    """Creating a table in a database"""
    with psycopg.connect(url) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                CREATE TABLE db_subscribtions (
                    id serial PRIMARY KEY,
                    user_id varchar(25),
                    chat_id varchar(25))
                """
            )
            conn.commit()


async def insert_db(url, values: tuple):
    """Adding a record to a table"""
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO db_subscribtions (
                    user_id,
                    chat_id)
                    VALUES (%s, %s)""",
                values,
            )

        conn.commit()


async def delete_subscribtions(url, values: tuple):
    """Removing entries from a table"""
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:

            cur.execute(
                """ SELECT id
                    FROM db_subscribtions
                    WHERE user_id = %s
                    AND chat_id = %s""",
                values,
            )
            rez = cur.fetchone()

            cur.execute(
                """ DELETE FROM db_subscribtions
                    WHERE id = %s""",
                (rez[0],),
            )

            conn.commit()


async def get_subscribtions_db(url, list_dialogs, user_id: int):
    """Geting a subscribtions from a table for a specific user"""
    with psycopg.connect(url) as conn:

        with conn.cursor() as cur:
            cur.execute(
                """ SELECT chat_id
                    FROM db_subscribtions
                    WHERE user_id = %s""",
                (str(user_id),),
            )

            subscribtions_db = cur.fetchall()

            return await get_user_subscribtions(
                subscribtions_db, list_dialogs, user_id
            )


async def get_user_subscribtions(
    subscribtions_db: tuple, list_dialogs, user_id: int
):
    """Bringing to the right format, to work with subscriptions"""
    user_subscribtions = {}
    user_subscribtions_list = {}

    if subscribtions_db is None:
        return {}

    for tuple_chat_id in subscribtions_db:

        for chat_id in tuple_chat_id:

            chat_name = await get_chat_name(list_dialogs, chat_id)
            user_subscribtions_list[chat_id] = chat_name

    user_subscribtions[user_id] = user_subscribtions_list

    return user_subscribtions


async def get_chat_name(list_dialogs, chat_id: str):
    """Getting the current chat name"""
    for dialog in list_dialogs:
        if str(dialog.chat.id) == chat_id:
            return dialog.chat.title
