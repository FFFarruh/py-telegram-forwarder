import logging

from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from repositories import delete_subscribtions, get_subscribtions_db, insert_db
from settings import Settings

setting = Settings()


async def help_command(client: Client) -> None:
    """Output of the instructions for use"""
    await client.send_message(
        setting.target_id,
        "/help - Output a list of available commands.\n"
        "To add or remove subscriptions, write the name of the chat group\n",
    )


async def echo_message(client: Client, message: Message, list_dialogs) -> None:
    """Forward a message from other chats to a personal chat with the user"""
    user_subscribtions = await get_subscribtions_db(
        list_dialogs, message.from_user.id
    )

    if message.from_user.id in user_subscribtions:
        from_user_id = user_subscribtions[message.from_user.id]

    else:
        return

    if message.chat.id == setting.target_id:
        logging.info("Message echo ignored: Message from target chat")
        return

    elif str(message.chat.id) not in from_user_id:
        logging.info("Message echo ignored: This chat missing in white-list")
        return

    await client.forward_messages(
        setting.target_id, message.chat.id, message.message_id
    )


async def add_or_remove(message: Message, list_dialogs) -> str:
    """Adds or removes a subscription to the chat, relative to its status"""
    user_id = get_user_id(message)
    chat_id = await get_chat_id(message.text, list_dialogs)

    if not await is_chat(message.text, list_dialogs):
        return "No such chat-group were found"

    elif await is_subscribed(user_id, chat_id, list_dialogs):
        return await unsubscribe_from_chat(user_id, chat_id, message.text)

    else:
        return await subscribe_to_chat(
            user_id, chat_id, message.text, list_dialogs
        )


async def display_subscriptions(
    client: Client, user_id: int, response: str, list_dialogs
) -> None:
    """Displaying a list of subscriptions to the user"""
    subscribtions_list = response + "\n\n📝A list of your subscriptions:📝\n\n"
    subscribtions_dict = await get_subscribtions(user_id, list_dialogs)

    if subscribtions_dict == {}:
        subscribtions_list += "Empty"

    else:

        for id_ in subscribtions_dict:
            subscribtions_list += f"🟢{subscribtions_dict[id_]}\n"

    await client.send_message(user_id, subscribtions_list)


async def is_subscribed(user_id: int, chat_id: int, list_dialogs) -> bool:
    """Determining whether there is a subscription to the chat room"""
    subscribtions = await get_subscribtions(user_id, list_dialogs)
    return await check_subscrib(subscribtions, chat_id)


def get_user_id(message: Message) -> int:
    """Getting the id of the user in which the message was written"""
    return message.from_user.id


async def get_subscribtions(user_id: int, list_dialogs) -> dict:
    """Getting the dictionary with user subscriptions"""
    await is_user(user_id, list_dialogs)
    user_subscribtions = await get_subscribtions_db(list_dialogs, user_id)
    return user_subscribtions[user_id]


async def check_subscrib(subscribtions: list, chat_id: int) -> bool:
    """Check if there is a subscription to the chat room with this id"""

    for subscribtion in subscribtions:

        if subscribtion == str(chat_id):
            return True

    return False


async def subscribe_to_chat(
    user_id: int, chat_id: int, message_text: str, list_dialogs
) -> str:
    """Subscribe to chat to update"""
    user_subscribtions = await get_subscribtions_db(list_dialogs, user_id)
    user_subscribtions_list = user_subscribtions[user_id]
    user_subscribtions_list[chat_id] = message_text
    await insert_db((str(user_id), str(chat_id)))

    return f"You've been subscribed to {message_text}"


async def unsubscribe_from_chat(
    user_id: int, chat_id: int, message_text: str
) -> str:
    """Unsubscribe from chat with updates"""
    await delete_subscribtions((str(user_id), str(chat_id)))

    return f"You are unsubscribed from {message_text}"


async def get_chat_id(message_text: str, list_dialogs) -> int:
    """Getting the id of the chat in which the message was written"""
    for dialog in list_dialogs:
        if dialog.chat.title == message_text:
            return dialog.chat.id


async def is_chat(message_text: str, list_dialogs) -> bool:
    """Is there a chat room with this name"""
    for dialog in list_dialogs:
        if dialog.chat.title == message_text:
            return True
    return False


async def is_user(user_id: int, list_dialogs) -> None:
    """Check if such a user exists, if not, create"""
    user_subscribtions = await get_subscribtions_db(list_dialogs, user_id)
    if user_id in user_subscribtions:
        return
    else:
        user_subscribtions[user_id] = {}
        return
