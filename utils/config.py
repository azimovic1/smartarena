import os
import logging

TOKEN = os.environ.get('TOKEN')
DEBUG = int(os.environ.get("DEBUG", 1))
if DEBUG:
    TOKEN = "7100075678:AAHn_RUYuEcMLtIC7E4ZE_rbTvCAJzGNZEk"
    log_level = logging.INFO

else:
    log_level = logging.WARNING
    TOKEN = os.environ.get('TOKEN')

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
regions_file_path = os.path.join(BASE_DIR, "regions.json")

add_stadium_text = """<b>Stadion yaratish uchun quydagi malumotlar kerak boladi</b>
<i>-Stadion Nomi</i>
<i>-Kantakt malumotlari</i>
<i>-Stadion Rasmlar</i>
<i>-Narxi (soatiga)</i>
<i>-Ochilish vaqti</i>
<i>-Yopilish vaqti</i>
<i>-Viloyat</i>
<i>-Tuman</i>
<i>-Lakatsiya</i>
"""


def get_stadium_data_text(data):
    name = data["stadium_name"]
    desc = data["stadium_description"]
    price = int(data["stadium_price"])
    open_time = data["stadium_open_time"]
    close_time = data["stadium_close_time"]
    region = data["region_name"]
    district = data["district_name"]
    stadium_data = f"""<b>Nomi:</b> <code>{name}</code>
<b>Stadion haqida:</b>
<i>{desc}</i>

<b>Narxi:</b> <code>{price} </code>so'm/soat
<b>Ochilish vaqti:</b><code> {open_time}</code>
<b>Yopilish vaqti:</b> <code>{close_time}</code>
<b>Viloyat/shahar:</b> <code>{region}</code>
<b>Tuman:</b> <code>{district}</code>"""
    return stadium_data


def check_manage_sts_edit(call):
    result = "manage" in call.data and len(set(call.data.split("|")).difference({"refr", "del"}).intersection(
        {"name", "desc", "image", "price", "otime", "ctime", "reg", "dist", "loc"})) > 0
    return result


def admin_check_manage_sts_edit(call):
    result = "managa" in call.data and len(set(call.data.split("|")).difference({"refr", "del"}).intersection(
        {"name", "desc", "image", "price", "otime", "ctime", "reg", "dist", "loc"})) > 0
    return result


def check_all_manage_sts_edit(call):
    result = "manage" in call.data and len(set(call.data.split("|")).intersection(
        {"name", "desc", "image", "price", "otime", "ctime", "reg", "dist", "loc", "refr", "del"})) > 0
    return result


def admin_check_all_manage_sts_edit(call):
    result = "managa" in call.data and len(set(call.data.split("|")).intersection(
        {"name", "desc", "image", "price", "otime", "ctime", "reg", "dist", "loc", "refr", "del"})) > 0
    return result


def filter_update_call_handler(call):
    result = len(set(call.data.split("|")).intersection({"ows_time", "owreg", "owdist"})) > 0
    return result


def admin_filter_update_call_handler(call):
    result = len(set(call.data.split("|")).intersection({"ads_time", "adreg", "addist"})) > 0
    return result


def register_confirmation(name, number, check: bool):
    text = f"""<b>Ismi:</b> <code>{name}</code> 
<b>Telefon raqami:</b> <code>{number}</code>"""
    text_fail = "Noto'g'ri raqam kiritdingiz! yoki raqam ro'yhatdan o'tkazilgan\nTo'gri raqam formati: <b>+998901234567</b>\nqaytadan urinib ko'ring"
    return text if check else text_fail


def register_success(is_confirmed: bool, check: bool, username: str = None, number: str = None,
                     telegram_id: int = None):
    text = (f"Ro'yhatdan o'tdingiz.\n"
            f"Malumotlar:\n"
            f"Ism Family: <code>{username}</code>\n"
            f"Telefon Raqam: <code>{number}</code>", "Tasiqlandi")
    text_fail = ("Hatolik yuz berdi\nQaytadan urinib ko\'ring", "Hatolik yuzberdi")
    text_reject = ("Ismingizni kiriting.", "Malumotlarni qaytadan kiriting")
    if is_confirmed and check:
        return text
    elif not is_confirmed and check:
        return text_reject
    else:
        return text_fail
