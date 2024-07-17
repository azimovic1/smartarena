from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import json


def confirmation():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Tasdiqlash✅", callback_data="adconfirm"))
    markup.add(InlineKeyboardButton("O\'zgartirish✏️", callback_data="adreject"))
    return markup


def date_time():
    markup = InlineKeyboardMarkup()
    today = datetime.datetime.today().date()

    end_date = today + datetime.timedelta(days=20)

    date_range = [today + datetime.timedelta(days=x) for x in range((end_date - today).days + 1)]
    row_buttons = []
    for date in date_range:
        row_buttons.append(
            InlineKeyboardButton(date.strftime("%d-%b"), callback_data=f"addate|{date.strftime('%Y:%m:%d')}"))

        if len(row_buttons) == 3:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:  # Add the remaining buttons if any
        markup.row(*row_buttons)
    return markup


def regions_inline(for_add=0):
    from utils.config import regions_file_path
    markup = InlineKeyboardMarkup(row_width=2)
    with open(regions_file_path, "r", encoding="utf-8") as data:
        regions = json.load(data)["regions"]
    for i in range(0, len(regions), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(regions):
                region = regions[i + j]
                region_id = region["id"]
                region_name = region["name"]
                if for_add == 0:
                    row_buttons.append(InlineKeyboardButton(region_name, callback_data=f"adreg|{region_id}"))
                elif for_add == 1:
                    row_buttons.append(InlineKeyboardButton(region_name, callback_data=f"add_reg|{region_id}"))

        markup.row(*row_buttons)
    return markup


def district_inline(region_id, for_add=0):
    from utils.config import regions_file_path
    markup = InlineKeyboardMarkup(row_width=2)

    with open(regions_file_path, "r", encoding="utf-8") as data:
        districts = json.load(data)["districts"]

    row_buttons = []
    for district in districts:
        if district["region_id"] == region_id:
            district_id = district["id"]
            district_name = district["name"]
            if for_add == 0:
                row_buttons.append(InlineKeyboardButton(district_name, callback_data=f"addist|{district_id}"))
            else:
                row_buttons.append(InlineKeyboardButton(district_name, callback_data=f"add_dist|{district_id}"))

            if len(row_buttons) == 2:
                markup.row(*row_buttons)
                row_buttons = []

    if row_buttons:  # Add the remaining buttons if any
        markup.row(*row_buttons)

    return markup


def start_time_inline():
    markup = InlineKeyboardMarkup(row_width=3)

    day_times = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                 "19:00", "20:00", "21:00", "22:00", "23:00", "00:00"]

    row_buttons = []
    for time in day_times:

        row_buttons.append(InlineKeyboardButton(time, callback_data=f"ads_time|{time}"))

        if len(row_buttons) == 3:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        markup.row(*row_buttons)

    return markup


def hours_inline():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton("1", callback_data="adhour|1"), InlineKeyboardButton("2", callback_data="adhour|2"),
               InlineKeyboardButton("3", callback_data="adhour|3"))
    return markup


def stadiums_inline(stadiums):
    markup = InlineKeyboardMarkup(row_width=1)
    for stadium in stadiums:
        button_text = stadium.name
        callback_data = f"adbook|{stadium.id}"

        button = InlineKeyboardButton(button_text, callback_data=callback_data)
        markup.add(button)

    return markup


def book_inline(bron=False):
    markup = InlineKeyboardMarkup()
    if bron:
        markup.row(InlineKeyboardButton("Bron qilish☑️", callback_data="adbook_now"))
        return markup
    else:
        markup.row(InlineKeyboardButton("Bron qilish☑️", callback_data="adbook_now"),
                   InlineKeyboardButton("Lakatsiyani ko'rish📍", callback_data="adsend_loc"))
        return markup


def yes_no_inline():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Ha✅", callback_data="adproceed|1"),
               InlineKeyboardButton("Yo'q❌", callback_data="adproceed|0"))
    return markup


def stadiums_choose(stadiums):
    markup = InlineKeyboardMarkup(row_width=2)
    for stadium in stadiums:
        markup.add(InlineKeyboardButton(stadium[0], callback_data=f"adstadium|{stadium[1]}"))
    return markup


def booked_stadiums_choose(stadiums):
    markup = InlineKeyboardMarkup(row_width=2)
    for stadium in stadiums:
        markup.add(InlineKeyboardButton(stadium[0], callback_data=f"ad_book|{stadium[1]}"))
    return markup


def manage_stadium(s_id):
    markup = InlineKeyboardMarkup()
    name = InlineKeyboardButton("Nomi✏️", callback_data=f"managa|name|{s_id}")
    desc = InlineKeyboardButton("Ma'lumotlari✏️", callback_data=f"managa|desc|{s_id}")
    image = InlineKeyboardButton("Rasmlari✏️", callback_data=f"managa|image|{s_id}")
    price = InlineKeyboardButton("Narxi✏️", callback_data=f"managa|price|{s_id}")
    opening = InlineKeyboardButton("Ochilish vaqti✏️", callback_data=f"managa|otime|{s_id}")
    closing = InlineKeyboardButton("Yopilish vaqti✏️", callback_data=f"managa|ctime|{s_id}")
    region = InlineKeyboardButton("Viloyati✏️", callback_data=f"managa|reg|{s_id}")
    district = InlineKeyboardButton("Tumani✏️", callback_data=f"managa|dist|{s_id}")
    location = InlineKeyboardButton("Lokatsiya✏️", callback_data=f"managa|loc|{s_id}")
    refresh = InlineKeyboardButton("Yangilash🔄", callback_data=f"managa|refr|{s_id}")
    delete = InlineKeyboardButton("Stadionni o'chirish❌", callback_data=f"managa|del|{s_id}")
    markup.row(name, desc)
    markup.row(image, price)
    markup.row(opening, closing)
    markup.row(region, district)
    markup.row(location)
    markup.row(refresh, delete)
    return markup
