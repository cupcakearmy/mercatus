from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext

from commands.other import stop_handler
from constants import Section

MENU, API_KEY, ENABLED, DELETE = map(chr, range(4))


def init(update: Update, context: CallbackContext):
    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )
    return show_menu(update, context)


def show_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('API Key', callback_data=API_KEY)],
        [InlineKeyboardButton(
            f'Turn {"off" if context.user_data.setdefault(Section.Enabled.value, True) else "on"} global auto updates',
            callback_data=ENABLED)],
        [InlineKeyboardButton('Delete all data', callback_data=DELETE)],
        [InlineKeyboardButton('Done', callback_data=ConversationHandler.END)],
    ]
    update.effective_user.send_message(
        '_Current settings:_\n'
        f'API Key: *{context.user_data.get(Section.API_Key.value, "No API key set")}*\n'
        f'Global auto updates: *{context.user_data[Section.Enabled.value]}*\n'
        '\nWhat settings do you want to configure?',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

    return MENU


def menu(update: Update, context: CallbackContext):
    selected = update.callback_query.data

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    if selected == API_KEY:
        return show_api_key(update, context)
    elif selected == ENABLED:
        toggle_enabled(update, context)
    elif selected == DELETE:
        return show_delete(update, context)
    else:
        return ConversationHandler.END


def show_delete(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('Yes', callback_data='1')],
        [InlineKeyboardButton('Back', callback_data='0')],
    ]
    update.effective_user.send_message(
        '🗑 Are you sure? Cannot be undone!',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return DELETE


def delete(update: Update, context: CallbackContext):
    selected = update.callback_query.data

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    if selected == '1':
        stop_handler(update, context)
        return ConversationHandler.END
    else:
        return show_menu(update, context)


def show_api_key(update: Update, context: CallbackContext):
    update.effective_user.send_message(
        'Send me your API Key 🙂'
        '\nor /cancel',
        reply_markup=ReplyKeyboardRemove()
    )
    return API_KEY


def api_key(update, context):
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
            MessageHandler(Filters.text, api_key),
        ],
        DELETE: [CallbackQueryHandler(delete)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
