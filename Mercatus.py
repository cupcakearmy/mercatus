from asyncio import sleep
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler

from Background import interval
from Market import Market
from Utils import persistence, config, Section
from Commands import watchlist_add, watchlist_delete, watchlist_all, watchlist_clear, set_api_key, get_api_key

updater: Updater = Updater(config['token'], use_context=True, persistence=persistence)


@interval(every=1.0 * 60 * 60, autorun=False, isolated=True)
async def send_updates():
    delta = datetime.now() - timedelta(days=365 * 1)

    for key, data in persistence.get_user_data().items():
        if Section.API_Key.value not in data:
            continue

        market = Market(data[Section.API_Key.value])
        updater.bot.send_message(key, text='Getting updates 🌎')
        first = True
        for item in data.get(Section.Watchlist.value, []):
            if first:
                first = False
            else:
                msg = updater.bot.send_message(key, text='Waiting 60 seconds for API... ⏳')
                await sleep(60)
                msg.delete()

            msg = updater.bot.send_message(key, text='Calculating... ⏳')
            updater.bot.send_photo(key, photo=market.get_wma(item, delta))
            msg.delete()
            updater.bot.send_message(key, text=item)

    # Repeat after every hour
    # threading.Timer(1.0 * 60 * 60, send_updates).start()


def main():
    global updater
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('add', watchlist_add))
    dp.add_handler(CommandHandler('delete', watchlist_delete))
    dp.add_handler(CommandHandler('list', watchlist_all))
    dp.add_handler(CommandHandler('clear', watchlist_clear))
    dp.add_handler(CommandHandler('setKey', set_api_key))
    dp.add_handler(CommandHandler('getKey', get_api_key))

    print('Started 🚀')
    send_updates()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
