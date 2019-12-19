from enum import Enum

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext

MENU, API_KEY, ENABLED = range(3)


class Section(Enum):
    Watchlist = 'watchlist'  # The list of Stocks/ETF to watch
    Code = 'code'  # Market code for a given stock, etf, etc.
    API_Key = 'api_key'  # Alpha Vantage API Key
    Running = 'running'  # Currently sending updates. Avoid overloading the API
    Enabled = 'enabled'  # Whether the bot should send automatic updates
    Interval = 'interval'  # Time axis of the graph
    Frequency = 'frequency'  # How ofter updates should be sent
    LastRun = 'last_run'  # Last time an update was sent to the user
    CurrentToEdit = 'current_to_edit'  # Current element to edit in the conversation handler


def show_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('API Key', callback_data=API_KEY)],
        [InlineKeyboardButton(
            f'Turn {"off" if context.user_data.setdefault(Section.Enabled.value, True) else "on"} global auto updates',
            callback_data=ENABLED)],
        [InlineKeyboardButton('Done', callback_data=ConversationHandler.END)],
    ]
    update.effective_user.send_message(
        '_Current settings:_\n'
        f'API Key: *{context.user_data.get(Section.API_Key.value, "No Api key set")}*\n'
        f'Global auto updates: *{context.user_data[Section.Enabled.value]}*\n'
        '\nWhat settings do you want to configure?',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

    return MENU


def show_menu_api_key(update: Update, context: CallbackContext):
    update.effective_user.send_message(
        'Send me your API Key 🙂'
        '\nor /cancel',
        reply_markup=ReplyKeyboardRemove()
    )
    return API_KEY


def init(update: Update, context: CallbackContext):
    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )
    return show_menu(update, context)


def menu(update: Update, context: CallbackContext):
    selected = int(update.callback_query.data)

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    if selected == API_KEY:
        return show_menu_api_key(update, context)
    elif selected == ENABLED:
        toggle_enabled(update, context)
    else:
        return ConversationHandler.END


def set_api_key(update, context):
    reply = update.message.text
    context.user_data[Section.API_Key.value] = reply
    update.message.reply_text(f'Saved {reply} 💾', reply_markup=ReplyKeyboardRemove())

    return show_menu(update, context)


def toggle_enabled(update: Update, context: CallbackContext):
    context.user_data[Section.Enabled.value] = not context.user_data[Section.Enabled.value]

    return show_menu(update, context)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Canceled', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


config_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', init)],
    states={
        MENU: [CallbackQueryHandler(menu)],
        API_KEY: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.all, set_api_key),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
