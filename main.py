import logging

# Enable logging
from telegram.ext import CommandHandler, Updater, PicklePersistence

from dotenv import load_dotenv
from lib.bot import start, set_timer, unset, show_schedule, error_handler, subscribe_on_updates
from os import environ

import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
load_dotenv(".env")

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = environ.get('LOG_LEVEL', logging.INFO)
LOG_FILE = environ.get('LOG_FILE')

if LOG_FILE:
    logging.basicConfig(filename=LOG_FILE,
                        filemode='a',
                        format=LOG_FORMAT,
                        level=LOG_LEVEL)
else:
    logging.basicConfig(
        format=LOG_FORMAT, level=LOG_LEVEL
    )

logger = logging.getLogger(__name__)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='powercut.pickle')
    updater = Updater(environ['BOT_TOKEN'], persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    dispatcher.add_handler(CommandHandler("schedule", show_schedule))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_on_updates))
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
