import matplotlib as mpl
from telegram.ext import CommandHandler

from utils import updater
from commands.config import config_handler
from commands.watchlist import watchlist_handler
from commands.other import data, send_updates, start_handler, help_handler, stop_handler, error_handler


def main():
    # Setup
    mpl.use('agg')
    dp = updater.dispatcher
    jq = updater.job_queue

    # Handlers
    dp.add_error_handler(error_handler)
    dp.add_handler(CommandHandler('start', start_handler))
    dp.add_handler(CommandHandler('stop', stop_handler))
    dp.add_handler(CommandHandler('help', help_handler))
    dp.add_handler(CommandHandler('data', data))
    dp.add_handler(config_handler)
    dp.add_handler(watchlist_handler)

    # Cron jobs
    jq.run_repeating(send_updates, interval=30, first=5)

    # Start
    print('Started 🚀')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
