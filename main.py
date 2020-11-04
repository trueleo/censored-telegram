from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import database
from database import DataNotFound
import os
import re
import shortuuid
from telegram.utils import helpers

uuid_to_file_id = dict()

def handler_media(update, context):
    uuid = shortuuid.uuid()
    file_type = file_id = None

    if update.message.photo:
        file_type = 'photo'
        file_id = update.message.photo[0].file_id
    elif update.message.video:
        file_type = 'video'
        file_id = update.message.video.file_id
    elif update.message.text:
        update.message.reply_text(
            "Share any video or photo to create censored post")
        return
    else:
        update.message.reply_text("Media format is not supported yet")
        return

    tup = (file_id, file_type, update.message.caption)
    uuid_to_file_id[uuid] = tup
    database.push(uuid, *tup)

    url = helpers.create_deep_linked_url(context.bot.get_me().username, uuid)
    text = 'Censored Media'
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='View', url=url)
    )
    update.message.reply_text(text, reply_markup=keyboard)


def handler_args(update, context):
    uuid = context.args[0]
    media_not_found = False
    try:
        file_id, file_type, file_caption = uuid_to_file_id[uuid]
    except KeyError:
        try:
            (file_id, file_type, file_caption) = database.get(uuid)
        except DataNotFound:
            media_not_found = True
        except:
            media_not_found = True
            update.message.reply_text('Internal error')

    if media_not_found:
        update.message.reply_text('Media not found')
        return
    if file_type == 'photo':
        update.message.reply_photo(file_id, caption=file_caption)
    elif file_type == 'video':
        update.message.reply_video(file_id, caption=file_caption)
    else:
        update.message.reply_text('Unknown file')
    return


def start(update, context):
    update.message.reply_text(
        "Hello, Share any video or photo to create censored post. Documents and files are not supported yet.")


def main():

    updater = Updater(os.environ.get('BOTKEY'), use_context=True)

    handlers = [
        CommandHandler("start", handler_args, Filters.regex("start\ [0-9A-Za-z]{10,50}")),
        CommandHandler("start", start),
        MessageHandler(Filters.all, handler_media)
    ]

    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
