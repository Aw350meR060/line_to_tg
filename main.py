from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ParseMode
import logging
import re
import zipfile
from PIL import Image
import requests
from io import BytesIO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHECKING, WAITING, SELECTING_TYPE = range(3)

reply_yn = [['Yes', 'No']]
markup = ReplyKeyboardMarkup(reply_yn, one_time_keyboard=True)

reply_anim = [['Animated', 'Static']]
markup_anim = ReplyKeyboardMarkup(reply_anim, one_time_keyboard=True)


def main():
    updater = Updater(token='628057302:AAEbIYHfPzlndsrV3zWrT3RDR2aNRwwDnfo', use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('help', start),
                      CommandHandler('download', awaiting_id)],

        states={
            WAITING: [MessageHandler(Filters.text, check_pack)],
            SELECTING_TYPE: [MessageHandler(Filters.text, select_type)],
            CHECKING: [MessageHandler(Filters.text, parse_png)],
        },

        fallbacks=[CommandHandler(['cancel', 'done'], cancel)]
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


def start(update, context):
    update.message.reply_text(
        text="Hi there! I'm a bot that downloads sticker packs from LINE in a format optimized to Telegram! \n"
             "This is a test bot, it only downloads the images for you to forward them to official 'Stickers' bot. "
             "Integration of custom pack creation is in plans, so stay tuned!\n\n"
             "*Commands*\n"
             "/download - downloads a sticker pack\n"
             "/cancel or /done - cancels ongoing operation"
             "/help shows this message again", parse_mode=ParseMode.MARKDOWN)


def awaiting_id(update, context):
    update.message.reply_text(text="Okay, now send me an ID of the desired pack. You can find one in pack's URL. \n\n"
                                   "Example: https://store.line.me/stickershop/product/*0000000*/en",
                              parse_mode=ParseMode.MARKDOWN)
    return WAITING


def check_pack(update, context):
    if re.search(r'[a-z](?!__)\w+', update.message.text, re.IGNORECASE):
        update.message.reply_text(text="ID contains invalid symbols, please try again.")
        return WAITING

    context.user_data['pack_id'] = int(update.message.text)
    pack_id = context.user_data['pack_id']

    name_string = """"en":"""
    pack_meta = get_meta(pack_id, update, context).text
    context.user_data['pack_meta'] = pack_meta
    pack_name = get_pack_feature(name_string, pack_meta).strip()
    update.message.reply_text("Your sticker pack is '" + pack_name + "', right?", reply_markup=markup)
    return SELECTING_TYPE


def select_type(update, context):
    print('a')
    if update.message.text != 'Yes':
        update.message.reply_text(text="Okay, you can try again by sending /download.")
        return ConversationHandler.END

    pack_id = context.user_data['pack_id']
    pack_meta = get_meta(pack_id, update, context).text
    name_string = """"stickerResourceType":"""
    pack_type = get_pack_feature(name_string, pack_meta).strip()
    if pack_type == 'ANIMATION':
        update.message.reply_text("Do you wish your stickers to be animated or static?", reply_markup=markup_anim)
    return CHECKING


def parse_png(update, context):
    if update.message.text == 'Animated':
        anim = True
    else:
        anim = False

    pack_id = context.user_data['pack_id']
    images = get_png(pack_id, anim)
    i = 1

    for img in images:
        bio = BytesIO()
        if anim:
            bio.name = 'image{}.apng'.format(i)
            img.save(bio, 'APNG')
        else:
            bio.name = 'image{}.png'.format(i)
            img.save(bio, 'PNG')
        bio.seek(0)
        context.bot.send_document(chat_id=update.message.chat_id, document=bio)
        i += 1

    update.message.reply_text(
        text="Okay, that is all of the stickers. \n\nYou can download another sticker pack by sending /download")
    return ConversationHandler.END


def get_meta(pack_id, update, context):
    pack_url = "http://dl.stickershop.line.naver.jp/products/0/0/1/{}/iphone/productInfo.meta".format(pack_id)
    pack_meta = requests.get(pack_url)

    if pack_meta.status_code == 200:
        return pack_meta
    else:
        update.message.reply_text("Couldn't find requested sticker pack. Please re-check pack's ID.")


def get_pack_feature(name_string, pack_meta):
    start_index = pack_meta.find(name_string)
    end_index = pack_meta.find(',', start_index + 1)
    sticker_name = pack_meta[start_index + len(name_string) + 1:end_index - 1]
    return sticker_name


def get_png(pack_id, anim):
    if anim:
        url = 'http://dl.stickershop.LINE.naver.jp/products/0/0/1/{}/iphone/stickerpack@2x.zip'.format(pack_id)
    else:
        url = 'http://dl.stickershop.LINE.naver.jp/products/0/0/1/{}/iphone/stickers@2x.zip'.format(pack_id)
    r = requests.get(url, stream=True)
    archive = zipfile.ZipFile(BytesIO(r.content))
    zip_list = archive.namelist()

    img_list = []
    for x in zip_list:
        if anim:
            if 'animation' in x:
                image = Image.open(BytesIO(archive.read(x)))
                img_list.append(optimize(image))
        else:
            if 'key' not in x:
                image = Image.open(BytesIO(archive.read(x)))
                img_list.append(optimize(image))
    return img_list


def optimize(img):
    base_size = 512
    if img.size[0] > img.size[1]:
        size_per = base_size / (float(img.size[0]))
        new_size = int((float(img.size[1])) * float(size_per))
        new_img = img.resize((base_size, new_size), Image.ANTIALIAS)
    else:
        size_per = base_size / (float(img.size[1]))
        new_size = int((float(img.size[0])) * float(size_per))
        new_img = img.resize((new_size, base_size), Image.ANTIALIAS)
    return new_img


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(update, context):
    update.message.reply_text(text="Command was canceled. Send /download to try again")
    return ConversationHandler.END


if __name__ == '__main__':
    main()
