from telegram.ext import Filters, MessageHandler, Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from settings import Settings
import logging


def echo_message(update: Update, _context: CallbackContext) -> None:
    settings = Settings()
    chat_id = update.effective_message.chat_id

    if update.effective_message.chat_id == settings.user_id:
        logging.info("Message echo ignored: Message from target chat")
        return
    elif chat_id not in settings.from_chat_ids:
        logging.info("Message echo ignored: This chat missing in white-list")
        return

    message_id = update.effective_message.message_id
    update.message.bot.forward_message(settings.user_id, chat_id, message_id)


updater = Updater(Settings().telegram_bot_token)
updater.dispatcher.add_handler(MessageHandler(Filters.text, echo_message))


updater.start_polling()
updater.idle()
