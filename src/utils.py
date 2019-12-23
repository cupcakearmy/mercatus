from datetime import datetime, timedelta
from enum import Enum

from yaml import load, Loader
from telegram import Update
from telegram.ext import PicklePersistence, Updater

DB_FILE = './data.db'
CONFIG_FILE = './config.yml'

config = load(open(CONFIG_FILE, 'r'), Loader=Loader)
persistence = PicklePersistence(DB_FILE)
updater: Updater = Updater(config['token'], use_context=True, persistence=persistence)


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
