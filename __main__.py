from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from settings import Settings
import logging

setting = Settings()
client = Client("", setting.api_id, setting.api_hash)


@client.on_message()
async def echo_message(client: Client, message: Message) -> None:
    global setting
    if message.chat.id == setting.target_id:
        logging.info("Message echo ignored: Message from target chat")
        return
    elif message.chat.id not in setting.from_chat_ids:
        logging.info("Message echo ignored: This chat missing in white-list")
        return
    await client.forward_messages(
        setting.target_id, message.chat.id, message.message_id
    )


client.run()
