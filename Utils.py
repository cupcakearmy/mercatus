from telegram import Update
from telegram.ext import PicklePersistence
from yaml import load, Loader
from enum import Enum

config = load(open('./config.yml', 'r'), Loader=Loader)
persistence = PicklePersistence('./data/mercatus')


class Section(Enum):
    Watchlist = 'watchlist'
    API_Key = 'api_key'


def parse_command(update: Update) -> (str, str):
    key, value = (update.message.text.split(' ', 1)[1].split(' ', 1) + [None])[:2]
    return key, value
