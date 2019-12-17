from asyncio import sleep, run
from datetime import datetime
from threading import Timer

from pytimeparse import parse
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async

from market import Market
from text import INTRO_TEXT
from utils import Section, persistence, updater, current_timestamp, delta_timestamp

SENDING = False


def error(update: Update, context: CallbackContext):
    print(context.error)


def start(update: Update, context: CallbackContext):
    update.message.reply_markdown(INTRO_TEXT)


@run_async
def data(update: Update, context: CallbackContext):
    delta = current_timestamp() - context.user_data.setdefault(Section.Interval.value, delta_timestamp(days=365))
    send_update_to_user(user=update.effective_user['id'], delta=delta)


def send_update_to_user(user: str, delta: int):
    user_data = None
    try:
        user_data = persistence.user_data[user]
        running = user_data.setdefault(Section.Running.value, False)
        print(f'Running {user} - {user_data}')

        if Section.API_Key.value not in user_data:
            updater.bot.send_message(user, text='API Key not set ⛔️')
            return

        if running:
            updater.bot.send_message(user, text='Already running 🏃')
            return

        print(f'Sending updates to {user}')
        user_data[Section.Running.value] = True
        user_data[Section.LastRun.value] = current_timestamp()

        market = Market(user_data[Section.API_Key.value])
        updater.bot.send_message(user, text='Getting updates 🌎')

        first = True
        for item in user_data.get(Section.Watchlist.value, []):
            if first:
                first = False
            else:
                # Wait to not overload the api
                msg = updater.bot.send_message(user, text='Waiting 60 seconds for API... ⏳')
                run(sleep(60))
                msg.delete()

            msg = updater.bot.send_message(user, text=f'Calculating {item}... ⏳')
            chart = market.get_wma(item, datetime.fromtimestamp(delta))
            msg.delete()
            updater.bot.send_photo(user, photo=chart, caption=f'*{item}*',
                                   parse_mode=ParseMode.MARKDOWN, disable_notification=True)

    except Exception as e:
        print(f'❌ {user} - {e}')
        updater.bot.send_message(user, text=f'There was an error ⚠️\n {e}')
    finally:
        if user_data:
            user_data[Section.Running.value] = False


def send_updates(context: CallbackContext):
    global SENDING
    try:
        if SENDING:
            return

        SENDING = True
        now = current_timestamp()

        for user, user_data in persistence.user_data.items():
            enabled = user_data.setdefault(Section.Enabled.value, True)
            last_run = user_data.setdefault(Section.LastRun.value, 0)
            frequency = parse(user_data.setdefault(Section.Frequency.value, '1d'))

            if enabled and last_run + frequency < now:
                delta = now - user_data.setdefault(Section.Interval.value, delta_timestamp(days=365))
                send_update_to_user(user=user, delta=delta)
    except Exception as e:
        print(e)
    finally:
        SENDING = False
