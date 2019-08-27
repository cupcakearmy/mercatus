from telegram import Update
from telegram.ext import PicklePersistence, Updater
from yaml import load, Loader
from enum import Enum
import pickle

DB_FILE = './data.db'
CONFIG_FILE = './config.yml'
DEFAULT_DATA = {
    'user_data': {},
    'chat_data': {},
    'conversations': {},
}

try:
    pickle.load(open(DB_FILE, 'rb'))
except:
    pickle.dump(DEFAULT_DATA, open(DB_FILE, 'wb'))

config = load(open(CONFIG_FILE, 'r'), Loader=Loader)
persistence = PicklePersistence(DB_FILE)
updater: Updater = Updater(config['token'], use_context=True, persistence=persistence)


class Section(Enum):
    Watchlist = 'watchlist'
    API_Key = 'api_key'
    Running = 'running'


def parse_command(update: Update) -> (str, str):
    key, value = (update.message.text.split(' ', 1)[1].split(' ', 1) + [None])[:2]
    return key, value
