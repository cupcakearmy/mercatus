from datetime import datetime, timedelta
from enum import Enum

from yaml import load, Loader
from telegram import Update
from telegram.ext import PicklePersistence, Updater

DB_FILE = './data.db'
CONFIG_FILE = './config.yml'

config = load(open(CONFIG_FILE, 'r'), Loader=Loader)
persistence = PicklePersistence(DB_FILE)
# persistence.load_singlefile()
updater: Updater = Updater(config['token'], use_context=True, persistence=persistence)


class Section(Enum):
    Watchlist = 'watchlist'
    API_Key = 'api_key'
    Running = 'running'
    Interval = 'interval'  # Time axis of the graph
    Frequency = 'frequency'  # How ofter updates should be sent
    LastRun = 'last_run'


def current_timestamp():
    return int(datetime.now().timestamp())


def delta_timestamp(**kwargs):
    return int(timedelta(**kwargs).total_seconds())


def parse_command(update: Update) -> (str, str):
    key, value = (update.message.text.split(' ', 1)[1].split(' ', 1) + [None])[:2]
    return key, value


def parse_callback(update: Update) -> str:
    selected = update.callback_query.data
    cleaned = ''.join(selected.split(':')[1:])  # Remove the pattern from the start
    return cleaned
