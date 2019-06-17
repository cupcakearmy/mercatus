from telegram.ext import CommandHandler

from Utils import updater
from Commands import watchlist_add, watchlist_delete, watchlist_all, watchlist_clear, \
    set_api_key, get_api_key, start, data, send_updates


def main():
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('add', watchlist_add))
    dp.add_handler(CommandHandler('delete', watchlist_delete))
    dp.add_handler(CommandHandler('list', watchlist_all))
    dp.add_handler(CommandHandler('clear', watchlist_clear))
    dp.add_handler(CommandHandler('setkey', set_api_key))
    dp.add_handler(CommandHandler('getkey', get_api_key))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('data', data))

    print('Started 🚀')
    send_updates()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
