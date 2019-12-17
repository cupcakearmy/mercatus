import matplotlib as mpl
from telegram.ext import CommandHandler

from utils import updater, persistence
from commands.config import config_handler
from commands.watchlist import watchlist_add, watchlist_delete, watchlist_all, watchlist_clear
from commands.other import start, data, send_updates


def main():
    # Setup
    mpl.use('agg')
    dp = updater.dispatcher
    jq = updater.job_queue

    # Handlers
    dp.add_handler(CommandHandler('add', watchlist_add))
    dp.add_handler(CommandHandler('delete', watchlist_delete))
    dp.add_handler(CommandHandler('list', watchlist_all))
    dp.add_handler(CommandHandler('clear', watchlist_clear))
    dp.add_handler(config_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('data', data))

    # Cron jobs
    jq.run_repeating(send_updates, interval=30, first=0)

    # Start
    print('Started 🚀')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
