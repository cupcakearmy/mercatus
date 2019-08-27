import asyncio
from asyncio import sleep
from datetime import datetime, timedelta
from telegram.ext import CallbackContext
from telegram import Update, ParseMode

from Background import interval
from LimitedList import LimitedList
from Market import Market
from Utils import parse_command, config, Section, persistence, updater


def get_watchlist(context: CallbackContext) -> LimitedList:
    return LimitedList(context.user_data.setdefault(Section.Watchlist.value, []),
                       config[Section.Watchlist.value]['max_items'])


def watchlist_add(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    get_watchlist(context).add(value)
    update.message.reply_text('Saved 💾')


def watchlist_delete(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    update.message.reply_text('Deleted 🗑' if get_watchlist(context).delete(value) else 'Not found ❓')


def watchlist_all(update: Update, context: CallbackContext):
    items = get_watchlist(context).all()
    update.message.reply_text('\n'.join(items) if len(items) > 0 else 'Your list is empty 📭')


def watchlist_clear(update: Update, context: CallbackContext):
    get_watchlist(context).clear()
    update.message.reply_text('Cleared 🧼')


def set_api_key(update: Update, context: CallbackContext):
    value, *rest = parse_command(update)
    context.user_data[Section.API_Key.value] = value
    update.message.reply_text('API key saved 🔑')


def get_api_key(update: Update, context: CallbackContext):
    update.message.reply_text(context.user_data.get(Section.API_Key.value, 'API Key not set ⛔️'))


def data(update: Update, context: CallbackContext):
    id = update.message.chat_id
    delta = datetime.now() - timedelta(days=365 * 1)
    asyncio.run(send_update_to_user(user=id, delta=delta))


def start(update: Update, context: CallbackContext):
    update.message.reply_markdown("""*Welcome! 👋*

*1.* First you will need to get a (free) api token for the stock data.
[https://www.alphavantage.co/support/#api-key](Alphavantage Key 🔑)

*2.* Then enter it by sending the code to me with `/setKey myApiCode`

*3.* Add stocks or ETFs to your `/list` by going to [https://finance.yahoo.com/](Yahoo Finance 📈) and the sending it to `/add`
_Example_ For Apple `/add AAPL`

Enjoy 🚀
""")


async def send_update_to_user(user: str, delta: datetime):
    try:
        user_data = persistence.get_user_data()[user]
        running = user_data.setdefault(Section.Running.value, False)
        if Section.API_Key.value not in user_data:
            updater.bot.send_message(user, text='API Key not set ⛔️')
            return

        if running:
            updater.bot.send_message(user, text='Already running 🏃')
            return

        user_data[Section.Running.value] = True
        print('Sending updates to {}'.format(user))
        market = Market(user_data[Section.API_Key.value])
        updater.bot.send_message(user, text='Getting updates 🌎')
        first = True
        for item in user_data.get(Section.Watchlist.value, []):
            if first:
                first = False
            else:
                msg = updater.bot.send_message(user, text='Waiting 60 seconds for API... ⏳')
                await sleep(60)
                msg.delete()

            msg = updater.bot.send_message(user, text='Calculating {}... ⏳'.format(item))
            chart = market.get_wma(item, delta)
            msg.delete()
            updater.bot.send_message(user, text='*{}*'.format(item), parse_mode=ParseMode.MARKDOWN)
            updater.bot.send_photo(user, photo=chart)

    except:
        updater.bot.send_message(user, text='There was an error ⚠️')
    finally:
        user_data[Section.Running.value] = False


@interval(every=3 * 60 * 60.0, autorun=False, isolated=True)
async def send_updates():
    delta = datetime.now() - timedelta(days=365 * 1)

    for key in persistence.get_user_data().keys():
        await send_update_to_user(user=key, delta=delta)
