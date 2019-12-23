from datetime import datetime, timedelta
from os import environ, makedirs
from os.path import exists, dirname

from telegram import Update
from telegram.ext import PicklePersistence, Updater

DB_FILE = './data/db.pickle'
DB_DIR = dirname(DB_FILE)

if not exists(DB_DIR):
    makedirs(DB_DIR)

try:
    max_list_items = int(environ.get('MAX_LIST_SIZE'))
except:
    max_list_items = 8

token = environ.get('TOKEN')
if not token:
    raise Exception('No Token found.')

persistence = PicklePersistence(DB_FILE)
updater: Updater = Updater(token, use_context=True, persistence=persistence)


def update_updater_data():
    updater.dispatcher.user_data = persistence.user_data
    updater.dispatcher.update_persistence()
    persistence.flush()


def current_timestamp():
    return int(datetime.now().timestamp())


def delta_timestamp(**kwargs):
    return int(timedelta(**kwargs).total_seconds())


def parse_command(update: Update) -> (str, str):
    """
    Splits the command from the rest of the message and returns the tuple
    """
    key, value = (update.message.text.split(' ', 1)[1].split(' ', 1) + [None])[:2]
    return key, value
