import logging
from pyrogram import Client
from pyrogram.methods.messages import Messages
from app.settings import Settings
from app.services import (
    add_or_remove,
    create_db,
    display_subscriptions,
    echo_message,
    help_command,
)

setting = Settings()


# @client.on_message()
async def handle_message(client: Client, message: Messages) -> None:
    global setting
    if message.text == "/help" and message.chat.id == setting.target_id:
        logging.info("Run command help: Message from target chat")
        await help_command(client)
        return

    elif message.text == "/create db" and message.chat.id == setting.target_id:
        logging.info("Run command create db: Message from target chat")
        await create_db(setting.db_url)
        return

    elif message.chat.id == setting.target_id:
        logging.info("Run command add/remove: Message from target chat")
        response = await add_or_remove(client, message)
        await display_subscriptions(client, message.from_user.id, response)
        return

    await echo_message(client, message)
