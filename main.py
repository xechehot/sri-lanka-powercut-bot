import logging

# Enable logging
from telegram.ext import CommandHandler, Updater, PicklePersistence

from dotenv import dotenv_values
from lib.bot import start, set_timer, unset

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    config = dotenv_values(".env")
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='powercut.pickle')
    updater = Updater(config['BOT_TOKEN'], persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
