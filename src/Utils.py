from telegram import Update
from telegram.ext import PicklePersistence, Updater
from yaml import load, Loader
from enum import Enum

config = load(open('./config.yml', 'r'), Loader=Loader)
persistence = PicklePersistence('./data.db')
updater: Updater = Updater(config['token'], use_context=True, persistence=persistence)


class Section(Enum):
    Watchlist = 'watchlist'
    API_Key = 'api_key'
    Running = 'running'


def parse_command(update: Update) -> (str, str):
    key, value = (update.message.text.split(' ', 1)[1].split(' ', 1) + [None])[:2]
    return key, value
