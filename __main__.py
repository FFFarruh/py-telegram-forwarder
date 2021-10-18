from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from settings import Settings
import logging

setting = Settings()
client = Client("", setting.api_id, setting.api_hash)
from_chat_ids = []
user_subscribtions = {}


async def is_user(user_id: int) -> None:
    """Check if such a user exists, if not, create"""
    global user_subscribtions
    if user_id in user_subscribtions:
        return
    else:
        user_subscribtions[user_id] = {}
        return


async def help_command() -> None:
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

    if await is_subscribed(user_id, chat_id):
        return await unsubscribe_from_chat(user_id, chat_id, message.text)

    else:
        return await subscribe_to_chat(user_id, chat_id, message.text)


async def is_subscribed(user_id: int, chat_id: int) -> bool:
    """Determining whether there is a subscription to the chat room"""
    subscribtions = await get_subscribtions(user_id)
    return await check_subscrib(subscribtions, chat_id)


async def get_user_id(message: Message) -> int:
    """Getting the id of the user in which the message was written"""
    return message.from_user.id


async def get_subscribtions(user_id) -> dict:
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
    return f"Add {message_text}"


async def unsubscribe_from_chat(
    user_id: int, chat_id: int, message_text: str
) -> str:
    """Unsubscribe from chat with updates"""
    user_subscribtions_list = user_subscribtions[user_id]
    del user_subscribtions_list[chat_id]
    return f"Remove {message_text}"


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
