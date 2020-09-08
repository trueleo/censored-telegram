from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
# import logging
import re
import os

from vasuki import generate_gibberish as gibname
from telegram.utils import helpers

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# logger = logging.getLogger(__name__)

key_to_file_id = dict()

PHOTO = 0
VIDEO = 1

def handler_media(update, context):
    sharekey  = gibname('large')
    if update.message.photo:
        file_id = update.message.photo[0].file_id
        key_to_file_id[sharekey] = (file_id, PHOTO, update.message.caption)
    elif update.message.video:
        file_id = update.message.video.file_id
        key_to_file_id[sharekey] = (file_id, VIDEO, update.message.caption)
    elif update.message.text:
        update.message.reply_text("Share any video or photo to create censored post")
        return
    else:
        update.message.reply_text("Media format is not supported yet")
        return


    url = helpers.create_deep_linked_url(context.bot.get_me().username, sharekey)
    text = 'Censored Media'
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='View', url=url)
    )
    update.message.reply_text(text, reply_markup = keyboard)

def handler_args(update, context):
    sharekey = context.args[0]
    try:
        file_id, file_type, file_caption = key_to_file_id[sharekey]
        if file_type == PHOTO:
            update.message.reply_photo(file_id, caption=file_caption)
        if file_type == VIDEO:
            update.message.reply_video(file_id, caption=file_caption)

    except KeyError:
        update.message.reply_text('Media is no longer availible')
        return

def start(update, context):
    update.message.reply_text("Hello, Share any video or photo to create censored post. Documents and files are not supported yet.")

def main():

    updater = Updater(os.environ.get('BOTKEY'), use_context=True)

    handlers = [

        CommandHandler( "start", handler_args, Filters.regex("start(?=\ [a-z]+)")),
        CommandHandler( "start", start),
        MessageHandler( Filters.all, handler_media)

    ]

    for handler in handlers:
        updater.dispatcher.add_handler(handler)


    PORT = int(os.environ.get('PORT', '8443'))

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                           url_path=TOKEN)
    updater.bot.set_webhook("https://censortelebot.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
