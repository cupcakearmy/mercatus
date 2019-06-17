from telegram.ext import CallbackContext
from telegram import Update

from LimitedList import LimitedList
from Utils import parse_command, config, Section


def get_watchlist(context: CallbackContext) -> LimitedList:
    return LimitedList(context.user_data.setdefault(Section.Watchlist.value, []),
                       config[Section.Watchlist.value]['max_items'])


def watchlist_add(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    get_watchlist(context).add(value)
    update.message.reply_text('Saved 💾')


def watchlist_delete(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    update.message.reply_text('Deleted 🗑' if get_watchlist(context).delete(value) else 'Not found ❓')


def watchlist_all(update: Update, context: CallbackContext):
    items = get_watchlist(context).all()
    update.message.reply_text('\n'.join(items))


def watchlist_clear(update: Update, context: CallbackContext):
    get_watchlist(context).clear()
    update.message.reply_text('Cleared 🧼')


def set_api_key(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    context.user_data[Section.API_Key.value] = value
    update.message.reply_text('API key saved 🔑')


def get_api_key(update: Update, context: CallbackContext):
    update.message.reply_text(context.user_data.get(Section.API_Key.value, 'API Key not set'))
