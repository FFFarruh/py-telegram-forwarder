from pyrogram import Client
from pyrogram.methods.messages import Messages

from app.entrypoints import handle_message
from app.settings import Settings

setting = Settings()
client = Client("", setting.api_id, setting.api_hash)


@client.on_message()
async def start(client: Client, message: Messages) -> None:
    await handle_message(client, message)


client.run()
