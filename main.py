from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputMediaPhoto, InputMediaVideo
import database
import os
import asyncio
import shortuuid
from collections import defaultdict

bot_info = None

BOT_TOKEN = os.environ.get('BOTKEY')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

app = Client(api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

uuid_media = dict()
group_uuid = dict()

async def send_deeplink(message: Message, username: str, uuid: str):
    text = 'Censored Media'
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text='View', url="t.me/{0}/?start={1}".format(username, uuid))]
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message( filters.private & filters.media )
async def handler_media(client, message: Message):

    file_id = file_type = None
    uuid = None
    group = message.media_group_id

    for media_type in ("photo", "video", "animation"):
        try:
            media = getattr(message, media_type)
            file_id = media.file_id
            file_type = media_type
        except:
            continue

    if not file_id:
        await message.reply_text("Share any video, photo or gif to create censored post")
        return

    global bot_info
    if not bot_info:
        bot_info = await client.get_me()

    media_tup = (file_id, file_type, message.caption)

    if not group:
        uuid = shortuuid.uuid()
        uuid_media[uuid] = media_tup
        await send_deeplink(message, bot_info.username, uuid)
    else:
        try:
            uuid = group_uuid[group]
            uuid_media[uuid].append(media_tup)
        except KeyError:
            uuid = shortuuid.uuid()
            uuid_media[uuid] = [media_tup]
            group_uuid[group] = uuid
            await send_deeplink(message, bot_info.username, uuid)
    database.push(uuid, *media_tup)

@app.on_message(filters.command("start"))
async def handle_start(client, message: Message):

    try:
        uuid = message.command[1]
    except IndexError:
        await message.reply_text("Hello, Share any video or photo to create censored post. Documents and files are not supported yet.")
        return

    try:
        data = uuid_media[uuid]
    except KeyError:
        data = database.get(uuid)
        uuid_media[uuid] = data

    finally:
        if type(data) is tuple:
            (file_id, file_type, caption) = data
            if caption is None:
                await message.reply_cached_media(file_id)
            else:
                await message.reply_cached_media(file_id, caption=caption)

        elif type(data) is list:
            input_medias = []
            for file_id, file_type, caption in data:
                if (file_type == 'photo'):
                    input_medias.append(InputMediaPhoto(file_id, caption))
                elif (file_type == 'video'):
                    input_medias.append(InputMediaVideo(file_id, caption=caption))
            await message.reply_media_group( input_medias )

        else:
            await message.reply_text("Not found")


if __name__ == '__main__':
    app.run()
