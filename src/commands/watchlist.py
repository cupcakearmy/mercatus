from telegram import Update
from telegram.ext import CallbackContext

from limited_list import LimitedList
from utils import parse_command, config, Section


def get_watchlist(context: CallbackContext) -> LimitedList:
    return LimitedList(
        config[Section.Watchlist.value]['max_items'],
        context.user_data.setdefault(Section.Watchlist.value, []),
    )


def save_watchlist(context: CallbackContext, l: LimitedList):
    context.user_data[Section.Watchlist.value] = l.all()


def watchlist_add(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)

    wl = get_watchlist(context)
    wl.add(str(value).upper())
    save_watchlist(context, wl)
    update.message.reply_text('Saved 💾')


def watchlist_delete(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    wl = get_watchlist(context)
    found = wl.delete(value)
    save_watchlist(context, wl)
    update.message.reply_text('Deleted 🗑' if found else 'Not found ❓')


def watchlist_all(update: Update, context: CallbackContext):
    items = get_watchlist(context).all()
    update.message.reply_text('\n'.join(items) if len(items) > 0 else 'Your list is empty 📭')


def watchlist_clear(update: Update, context: CallbackContext):
    wl = get_watchlist(context)
    wl.clear()
    save_watchlist(context, wl)
    update.message.reply_text('Cleared 🧼')
