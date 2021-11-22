from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from settings import Settings
import logging
import psycopg

setting = Settings()
# client = Client("", setting.api_id, setting.api_hash)
from_chat_ids = []
user_subscribtions = {}


async def create_db():

    with psycopg.connect(setting.db_url) as conn:

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


async def insert_db(conn, values):

    with conn.cursor() as cur:

        cur.execute(
            "INSERT INTO db_subscribtions (user_id, chat_id) VALUES (%s, %s)",
            values,
        )

    conn.commit()


async def delete_subscribtions(conn, values):

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


async def is_user(user_id: int) -> None:
    """Check if such a user exists, if not, create"""
    global user_subscribtions
    if user_id in user_subscribtions:
        return
    else:
        user_subscribtions[user_id] = {}
        return


async def help_command(client: Client) -> None:
    """Output of the instructions for use"""
    await client.send_message(
        setting.target_id,
        "/help - Output a list of available commands.\n"
        "To add or remove subscriptions, write the name of the chat group\n",
    )


async def echo_message(client: Client, message: Message) -> None:
    """Forward a message from other chats to a personal chat with the user"""
    if message.from_user.id in user_subscribtions:
        from_user_id = user_subscribtions[message.from_user.id]
    else:
        return
    if message.chat.id == setting.target_id:
        logging.info("Message echo ignored: Message from target chat")
        return

    elif message.chat.id not in from_user_id:
        logging.info("Message echo ignored: This chat missing in white-list")
        return

    await client.forward_messages(
        setting.target_id, message.chat.id, message.message_id
    )


async def add_or_remove(client: Client, message: Message) -> str:
    """Adds or removes a subscription to the chat, relative to its status"""
    user_id = await get_user_id(message)
    chat_id = await get_chat_id(client, message.text)

    if not await is_chat(client, message.text):
        return "No such chat-group were found"

    elif await is_subscribed(user_id, chat_id):
        return await unsubscribe_from_chat(user_id, chat_id, message.text)

    else:
        return await subscribe_to_chat(user_id, chat_id, message.text)


async def display_subscriptions(
    client: Client, user_id: int, response: str
) -> None:
    """Displaying a list of subscriptions to the user"""
    subscribtions_list = response + "\n\n📝A list of your subscriptions:📝\n\n"
    subscribtions_dict = await get_subscribtions(user_id)

    if subscribtions_dict == {}:
        subscribtions_list += "Empty"

    else:

        for id_ in subscribtions_dict:
            subscribtions_list += f"🟢{subscribtions_dict[id_]}\n"

    await client.send_message(user_id, subscribtions_list)


async def is_subscribed(user_id: int, chat_id: int) -> bool:
    """Determining whether there is a subscription to the chat room"""
    subscribtions = await get_subscribtions(user_id)
    return await check_subscrib(subscribtions, chat_id)


async def get_user_id(message: Message) -> int:
    """Getting the id of the user in which the message was written"""
    return message.from_user.id


async def get_subscribtions(user_id: int) -> dict:
    """Getting the dictionary with user subscriptions"""
    global user_subscribtions
    await is_user(user_id)
    return user_subscribtions[user_id]


async def check_subscrib(subscribtions: list, chat_id: int) -> bool:
    """Check if there is a subscription to the chat room with this id"""

    for subscribtion in subscribtions:

        if subscribtion == chat_id:
            return True

    return False


async def subscribe_to_chat(
    user_id: int, chat_id: int, message_text: str
) -> str:
    """Subscribe to chat to update"""
    user_subscribtions_list = user_subscribtions[user_id]
    user_subscribtions_list[chat_id] = message_text

    with psycopg.connect(setting.db_url) as conn:
        await insert_db(conn, (str(user_id), str(chat_id)))

    return f"You've been subscribed to {message_text}"


async def unsubscribe_from_chat(
    user_id: int, chat_id: int, message_text: str
) -> str:
    """Unsubscribe from chat with updates"""
    user_subscribtions_list = user_subscribtions[user_id]
    del user_subscribtions_list[chat_id]
    with psycopg.connect(setting.db_url) as conn:
        await delete_subscribtions(conn, (str(user_id), str(chat_id)))

    return f"You are unsubscribed from {message_text}"


async def get_chat_id(client: Client, message_text: str) -> int:
    """Getting the id of the chat in which the message was written"""
    list_dialogs = await client.get_dialogs()
    for dialog in list_dialogs:
        if dialog.chat.title == message_text:
            return dialog.chat.id


async def is_chat(client: Client, message_text: str) -> bool:
    """Is there a chat room with this name"""
    list_dialogs = await client.get_dialogs()
    for dialog in list_dialogs:
        if dialog.chat.title == message_text:
            return True
    return False