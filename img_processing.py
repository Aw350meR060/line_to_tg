from PIL import Image
import requests
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def main(pack_id):
    id_string = """"id":"""
    name_string = """"en":"""

    pack_meta = get_meta(pack_id).text
    pack_name = get_pack_name(name_string, pack_meta).strip()
    print('Your sticker pack is "{}"?'.format(pack_name))

    ids = []
    current_id, start_index = 0, 0

    while start_index != -1:
        start_index, current_id, pack_meta = get_ids(id_string,
                                                     pack_meta)
        ids.append(current_id)
    ids.pop(len(ids)-1)

    images = get_png(ids)

def get_meta(pack_id):
    pack_url = "http://dl.stickershop.line.naver.jp/products/0/0/1/{}/android/productInfo.meta".format(pack_id)
    pack_meta = requests.get(pack_url)

    if pack_meta.status_code == 200:
        return pack_meta
    else:
        print("Couldn't find requested sticker pack. Please re-check pack's ID.")

def get_pack_name(name_string, pack_meta):
    start_index = pack_meta.find(name_string)
    end_index = pack_meta.find(',', start_index + 1)
    sticker_name = pack_meta[start_index+len(name_string)+1:end_index-1]
    return sticker_name

def get_png(list_ids):
    png_list = []
    for x in list_ids:
        url = 'http://dl.stickershop.line.naver.jp/stickershop/v1/sticker/{}/android/sticker.png'.format(x)
        r = requests.get(url, stream = True)
        image = Image.open(BytesIO(r.content))
        png_list.append(optimize(image))
    return png_list

def get_ids(id_string, pack_meta):
    start_index = pack_meta.find(id_string)
    end_index = pack_meta.find(",", start_index + 1)
    sticker_id = pack_meta[start_index+len(id_string):end_index]
    return start_index, sticker_id, pack_meta[end_index:]

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