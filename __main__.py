from telegram.ext import Filters, MessageHandler, Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

from settings import Settings


def start(update: Update, _context: CallbackContext) -> None:
    update.message.reply_text(" Hello World")


updater = Updater(Settings().telegram_bot_token)
updater.dispatcher.add_handler(MessageHandler(Filters.text, start))


updater.start_polling()
updater.idle()
