from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from settings import Settings
import logging

setting = Settings()
client = Client("", setting.api_id, setting.api_hash)
from_chat_ids = []
users_subscribtions = {667222186: {}}


async def help_command():
    await client.send_message(
        setting.target_id,
        "/help - Output a list of available commands.\n"
        "To add or remove subscriptions, write the name of the chat group\n",
    )


async def echo_message(client: Client, message: Message) -> None:
    from_user_id = users_subscribtions[message.from_user.id]

    if message.chat.id == setting.target_id:
        logging.info("Message echo ignored: Message from target chat")
        return

    elif message.chat.id not in from_user_id:
        logging.info("Message echo ignored: This chat missing in white-list")
        return

    await client.forward_messages(
        setting.target_id, message.chat.id, message.message_id
    )


async def add_or_remove(client: Client, message: Message) -> None:

    if not await is_chat(message.text):
        return "No such chat-group were found"

    if await is_subscribed(message):
        return await unsubscribe_from_chat(message)

    else:
        return await subscribe_to_chat(message)


async def is_subscribed(message: Message) -> bool:
    """Determining whether there is a subscription to the chat room"""
    user_id = await get_user_id(message)
    subscribtions = await get_subscribtions(user_id)
    return await check_subscrib(subscribtions, message)


async def get_user_id(message: Message):
    return message.from_user.id


async def get_subscribtions(user_id):
    return users_subscribtions[user_id]


async def check_subscrib(subscribtions: list, message: Message):
    chat_id = await get_chat_id(message)
    for subscribtion in subscribtions:
        if subscribtion == chat_id:
            return True
    return False


async def subscribe_to_chat(message: Message):
    """Subscribe to chat to update"""
    user_id = await get_user_id(message)
    chat_id = await get_chat_id(message)
    user_subscribtions = users_subscribtions[user_id]
    user_subscribtions[chat_id] = chat_id
    return f"Add {message.text}"


async def unsubscribe_from_chat(message: Message):
    """Unsubscribe from chat with updates"""
    user_id = await get_user_id(message)
    chat_id = await get_chat_id(message)
    user_subscribtions = users_subscribtions[user_id]
    del user_subscribtions[chat_id]
    return f"Remove {message.text}"


async def get_chat_id(message: Message):
    list_dialogs = await client.get_dialogs()
    for dialog in list_dialogs:
        if dialog.chat.title == message.text:
            return dialog.chat.id


async def is_chat(message_text: str) -> bool:
    list_dialogs = await client.get_dialogs()
    for dialog in list_dialogs:
        if dialog.chat.title == message_text:
            return True
    return False


@client.on_message()
async def handle_message(client: Client, message: Message) -> None:
    global setting
    if message.text == "/help" and message.chat.id == setting.target_id:
        logging.info("Run command help: Message from target chat")
        await help_command()
        return

    elif message.chat.id == setting.target_id:
        logging.info("Run command add/remove: Message from target chat")
        response = await add_or_remove(client, message)
        await client.send_message(setting.target_id, response)
        return

    await echo_message(client, message)


client.run()
