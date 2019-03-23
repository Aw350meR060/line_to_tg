import telegram
import logging
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def main():
    updater = Updater(token='628057302:AAEbIYHfPzlndsrV3zWrT3RDR2aNRwwDnfo')
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)

    dispatcher.add_handler(start_handler)
    updater.start_polling()

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="I'm a LINE Sticker pack transferring bot. What are you going to do?")

if __name__ == '__main__':
    main()