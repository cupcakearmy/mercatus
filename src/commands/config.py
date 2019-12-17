from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext

from utils import Section

MENU, API_KEY, FREQUENCY, ENABLED = range(4)


def show_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('API Key', callback_data=API_KEY)],
        [InlineKeyboardButton('Auto Updates', callback_data=ENABLED)],
        [InlineKeyboardButton('Frequency', callback_data=FREQUENCY)],
        [InlineKeyboardButton('Done', callback_data=ConversationHandler.END)],
    ]
    update.effective_user.send_message(
        '_Current settings:_\n'
        f'API Key: *{context.user_data[Section.API_Key.value]}*\n'
        f'Auto Updates: *{context.user_data[Section.Enabled.value]}*\n'
        f'Frequency: *{context.user_data[Section.Frequency.value]}*\n'
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


def show_menu_frequency(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('2 minutes', callback_data='2m'), InlineKeyboardButton(
            '30 minutes', callback_data='30m')],
        [InlineKeyboardButton('hour', callback_data='1h'), InlineKeyboardButton(
            '4 hours', callback_data='4h')],
        [InlineKeyboardButton('12 hours', callback_data='12h'), InlineKeyboardButton(
            'day', callback_data='1d')],
        [InlineKeyboardButton('3 days', callback_data='3d'), InlineKeyboardButton(
            'week', callback_data='1w')],
        [InlineKeyboardButton('Cancel', callback_data='cancel')],
    ]
    update.effective_user.send_message(
        'Send me updates every: ⬇',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return FREQUENCY


def config(update: Update, context: CallbackContext):
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
    elif selected == FREQUENCY:
        return show_menu_frequency(update, context)
    elif selected == ENABLED:
        toggle_enabled(update, context)
    else:
        return ConversationHandler.END


def set_api_key(update, context):
    reply = update.message.text
    context.user_data[Section.API_Key.value] = reply
    update.message.reply_text(f'Saved {reply} 💾', reply_markup=ReplyKeyboardRemove())

    return show_menu(update, context)


def set_frequency(update: Update, context: CallbackContext):
    selected = update.callback_query.data

    if selected != 'cancel':
        update.callback_query.edit_message_text(f'Saved {selected} 💪')
        context.user_data[Section.Frequency.value] = selected
    else:
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
        )

    return show_menu(update, context)


def toggle_enabled(update: Update, context: CallbackContext):
    new = not context.user_data.setdefault(Section.Enabled.value, True)
    context.user_data[Section.Enabled.value] = new
    update.effective_user.send_message('Auto updates enabled' if new else 'Auto updates disabled')

    return show_menu(update, context)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Canceled', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


config_handler = ConversationHandler(
    entry_points=[CommandHandler('config', config)],

    states={
        MENU: [CallbackQueryHandler(menu)],
        API_KEY: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.all, set_api_key),
        ],
        FREQUENCY: [CallbackQueryHandler(set_frequency)],
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
