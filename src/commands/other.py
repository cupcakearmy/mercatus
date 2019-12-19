from asyncio import sleep, run
from datetime import datetime

from pytimeparse import parse
from telegram import Update, ParseMode, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from telegram.ext.dispatcher import run_async

from commands.config import Section
from market import Market
from text import INTRO_TEXT
from utils import persistence, updater, current_timestamp, delta_timestamp

SENDING = False


def error_handler(update: Update, context: CallbackContext):
    print('Error: ', context.error)


def start_handler(update: Update, context: CallbackContext):
    update.message.reply_markdown(INTRO_TEXT)


def help_handler(update: Update, context: CallbackContext):
    update.message.reply_markdown(INTRO_TEXT)


def stop_handler(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text('You and your data were deleted 🗑')


@run_async
def data(update: Update, context: CallbackContext):
    send_update_to_user(update.effective_user['id'], False)


def send_update_to_user(user: str, auto, codes=None):
    user_data = None
    try:
        user_data = persistence.user_data[user]
        running = user_data.setdefault(Section.Running.value, False)

        if Section.API_Key.value not in user_data:
            updater.bot.send_message(user, text='API Key not set ⛔️\nSet in /settings')
            return

        if running:
            updater.bot.send_message(user, text='Already running 🏃')
            return

        user_data[Section.Running.value] = True
        market = Market(user_data[Section.API_Key.value])
        now = current_timestamp()
        if auto:
            updater.bot.send_message(user, text='Getting updates 🌎')

        first = True
        for code in codes if codes else user_data.get(Section.Watchlist.value, {}).keys():
            try:
                code_data = persistence.user_data[user][Section.Watchlist.value][code]
                code_data = code_data['value']
                print(code, code_data)
                last_run = code_data[Section.LastRun.value]
                frequency = parse(code_data[Section.Frequency.value])
                interval = parse(code_data[Section.Interval.value])
                print(code, last_run + frequency, now, last_run + frequency - now)

                if auto and last_run + frequency > now:
                    continue
                persistence.user_data[user][Section.Watchlist.value][code][Section.LastRun.value] = current_timestamp()
                persistence.flush()

                if first:
                    first = False
                else:
                    # Wait to not overload the api
                    msg = updater.bot.send_message(user, text='Waiting 60 seconds for API... ⏳')
                    run(sleep(60))
                    msg.delete()

                msg = updater.bot.send_message(user, text=f'Calculating {code}... ⏳')
                delta = datetime.fromtimestamp(now - interval)
                chart = market.get_wma(code, delta)
                msg.delete()
                updater.bot.send_photo(user, photo=chart, disable_notification=True,
                                       caption=f'{code} - {code_data[Section.Interval.value]}')
            except Exception as e:
                print(f'❌ {user} - {e}')
                updater.bot.send_message(user, text=f'There was an error ⚠️\n {e}')

        if auto:
            updater.bot.send_message(user, text=f'Done ✅')
    finally:
        if user_data:
            user_data[Section.Running.value] = False


def send_updates(context: CallbackContext):
    global SENDING
    try:
        if SENDING:
            return

        SENDING = True
        for user, user_data in persistence.user_data.items():
            if user_data.setdefault(Section.Enabled.value, False):
                send_update_to_user(user=user, auto=True)
    except Exception as e:
        print(e)
    finally:
        SENDING = False
