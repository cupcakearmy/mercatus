from telegram import Update, InlineKeyboardButton, ParseMode, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from commands.config import Section
from commands.other import send_update_to_user
from limited_dict import LimitedDict
from utils import parse_command, config

ALL, SINGLE, EDIT, ADD, DELETE, BACK, ENABLED, FREQUENCY, INTERVAL, DATA = map(chr, range(10))
END = str(ConversationHandler.END)


def get_watchlist(context: CallbackContext) -> LimitedDict:
    return LimitedDict(
        config[Section.Watchlist.value]['max_items'],
        context.user_data.setdefault(Section.Watchlist.value, {}),
    )


def save_watchlist(context: CallbackContext, limited_dict: LimitedDict):
    context.user_data[Section.Watchlist.value] = limited_dict.dict


def init(update: Update, context: CallbackContext):
    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )
    return show_menu(update, context)


def show_menu(update: Update, context: CallbackContext):
    wl = get_watchlist(context)
    saved = [
        [InlineKeyboardButton(item, callback_data=item)]
        for item in wl.all()
    ]
    options = [[
        InlineKeyboardButton('Add', callback_data=ADD),
        InlineKeyboardButton('Done', callback_data=END)
    ]]
    update.effective_user.send_message(
        '_Your Watchlist:_\n'
        f'*{len(wl)}/{wl.limit}* slots filled\n'
        '\nYou can add, modify or delete items',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(saved + options, one_time_keyboard=True)
    )

    return ALL


def menu(update: Update, context: CallbackContext):
    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    selected: str = update.callback_query.data
    if selected == ADD:
        return show_add(update, context)
    elif selected == END:
        return ConversationHandler.END
    else:
        context.user_data[Section.CurrentToEdit.value] = selected
        return show_single(update, context)


def show_add(update: Update, context: CallbackContext):
    update.effective_user.send_message(
        'Send me the code (e.g. AAPL or URTH)\n'
        'or send /cancel',
        reply_markup=ReplyKeyboardRemove()
    )
    return ADD


def add(update, context):
    reply: str = update.message.text
    wl = get_watchlist(context)
    wl[reply.upper()] = {
        Section.Enabled.value: True,
        Section.Frequency.value: '1d',
        Section.Interval.value: '52w',
        Section.LastRun.value: 0,
    }
    save_watchlist(context, wl)
    update.message.reply_text(f'Saved {reply} 💾', reply_markup=ReplyKeyboardRemove())

    return show_menu(update, context)


def show_single(update, context):
    current = context.user_data[Section.CurrentToEdit.value]
    current_data = get_watchlist(context)[current]
    keyboard = [
        [InlineKeyboardButton(f'Turn {"off" if current_data[Section.Enabled.value] else "on"} auto updates', callback_data=ENABLED)],
        [InlineKeyboardButton(f'Frequency', callback_data=FREQUENCY)],
        [InlineKeyboardButton(f'Time interval', callback_data=INTERVAL)],
        [InlineKeyboardButton(f'Show data', callback_data=DATA)],
        [InlineKeyboardButton('Delete', callback_data=DELETE)],
        [InlineKeyboardButton('Back', callback_data=BACK)],
    ]
    update.effective_user.send_message(
        '_Current settings:_\n'
        f'Auto Updates: *{current_data[Section.Enabled.value]}*\n'
        f'Frequency: *{current_data[Section.Frequency.value]}*\n'
        f'Interval: *{current_data[Section.Interval.value]}*\n'
        f'\nEdit {current}: ⬇',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return SINGLE


def single(update, context):
    current = context.user_data[Section.CurrentToEdit.value]
    selected = update.callback_query.data
    wl = get_watchlist(context)

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    if selected == DELETE:
        update.effective_user.send_message(f'Deleted {current} 💪')
        del wl[current]
        save_watchlist(context, wl)
        return show_menu(update, context)
    elif selected == BACK:
        return show_menu(update, context)
    elif selected == ENABLED:
        wl[current][Section.Enabled.value] = not wl[current][Section.Enabled.value]
        save_watchlist(context, wl)
        return show_single(update, context)
    elif selected == FREQUENCY:
        return show_single_frequency(update, context)
    elif selected == INTERVAL:
        return show_single_interval(update, context)
    elif selected == DATA:
        send_update_to_user(update.effective_user['id'], False, [current])
        return show_single(update, context)
    else:
        return cancel(update, context)


def show_single_frequency(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('5 minutes', callback_data='5m'), InlineKeyboardButton(
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


def single_frequency(update: Update, context: CallbackContext):
    return save_single_attribute(update, context, Section.Frequency.value)


def show_single_interval(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('1 day', callback_data='1d'), InlineKeyboardButton(
            '2 days', callback_data='2d')],
        [InlineKeyboardButton('1 week', callback_data='7d'), InlineKeyboardButton(
            '1 weeks', callback_data='14d')],
        [InlineKeyboardButton('1 month', callback_data='30d'), InlineKeyboardButton(
            '3 months', callback_data='90d')],
        [InlineKeyboardButton('1 year', callback_data='52w'), InlineKeyboardButton(
            '2 years', callback_data='104w')],
        [InlineKeyboardButton('Cancel', callback_data='cancel')],
    ]
    update.effective_user.send_message(
        'Select the graph time span 📈:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return INTERVAL


def single_interval(update: Update, context: CallbackContext):
    return save_single_attribute(update, context, Section.Interval.value)


def save_single_attribute(update: Update, context: CallbackContext, key):
    current = context.user_data[Section.CurrentToEdit.value]
    selected = update.callback_query.data
    wl = get_watchlist(context)

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    if selected != 'cancel':
        update.effective_user.send_message(f'Saved {selected} 💾')
        wl[current][key] = selected

    return show_single(update, context)


def cancel(update: Update, context: CallbackContext):
    update.effective_user.send_message('Canceled', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


cancel_command_handler = CommandHandler('cancel', cancel)

watchlist_handler = ConversationHandler(
    entry_points=[CommandHandler('list', init)],
    states={
        ALL: [CallbackQueryHandler(menu)],
        ADD: [cancel_command_handler, MessageHandler(Filters.text, add)],
        SINGLE: [cancel_command_handler, CallbackQueryHandler(single)],
        FREQUENCY: [CallbackQueryHandler(single_frequency)],
        INTERVAL: [CallbackQueryHandler(single_interval)],
    },
    fallbacks=[cancel_command_handler],
)
