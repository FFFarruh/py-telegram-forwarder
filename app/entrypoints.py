import logging

from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from services import (
    add_or_remove,
    display_subscriptions,
    echo_message,
    help_command,
)
from settings import Settings

setting = Settings()


async def handle_message(client: Client, message: Message) -> None:
    list_dialogs = await client.get_dialogs()
    if message.chat.id == setting.target_id:
        if message.text == "/help":
            logging.info("Run command help: Message from target chat")
            await help_command(client)
            return

        else:
            logging.info("Run command add/remove: Message from target chat")
            response = await add_or_remove(message, list_dialogs)
            await display_subscriptions(
                client, message.from_user.id, response, list_dialogs
            )
            return

    await echo_message(client, message, list_dialogs)
