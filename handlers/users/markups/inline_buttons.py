import datetime
import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirmation():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Tasdiqlash✅", callback_data="confirm|1"))
    markup.add(InlineKeyboardButton("O\'zgartirish✏️", callback_data="confirm|0"))
    return markup


def date_time():
    """:return: date markup with calldata 'date|{YY:MM:DD}'"""

    markup = InlineKeyboardMarkup()
    today = datetime.datetime.today().date()

    end_date = today + datetime.timedelta(days=20)

    date_range = [today + datetime.timedelta(days=x) for x in range((end_date - today).days + 1)]
    row_buttons = []
    for date in date_range:
        row_buttons.append(
            InlineKeyboardButton(date.strftime("%d-%b"), callback_data=f"date|{date.strftime('%Y:%m:%d')}"))

        if len(row_buttons) == 3:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        markup.row(*row_buttons)
    return markup


def regions_inline():
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
                row_buttons.append(InlineKeyboardButton(region_name, callback_data=f"region|{region_id}"))
        markup.row(*row_buttons)
    return markup


def district_inline(region_id):
    from utils.config import regions_file_path
    markup = InlineKeyboardMarkup(row_width=2)

    with open(regions_file_path, "r", encoding="utf-8") as data:
        districts = json.load(data)["districts"]

    row_buttons = []
    for district in districts:
        if district["region_id"] == region_id:
            district_id = district["id"]
            district_name = district["name"]
            row_buttons.append(InlineKeyboardButton(district_name, callback_data=f"district|{district_id}"))
            if len(row_buttons) == 2:
                markup.row(*row_buttons)
                row_buttons = []

    if row_buttons:
        markup.row(*row_buttons)

    return markup


def start_time_inline():
    markup = InlineKeyboardMarkup(row_width=3)

    day_times = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                 "19:00", "20:00", "21:00", "22:00", "23:00", "00:00"]

    row_buttons = []
    for time in day_times:
        row_buttons.append(InlineKeyboardButton(time, callback_data=f"start_time|{time}"))

        if len(row_buttons) == 3:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        markup.row(*row_buttons)

    return markup


def hours_inline():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton("1", callback_data="hour|1"), InlineKeyboardButton("2", callback_data="hour|2"),
               InlineKeyboardButton("3", callback_data="hour|3"))
    return markup


def stadiums_inline(stadiums):
    markup = InlineKeyboardMarkup(row_width=1)
    for stadium in stadiums:
        button_text = stadium.name
        callback_data = f"book|{stadium.id}"

        button = InlineKeyboardButton(button_text, callback_data=callback_data)
        markup.add(button)

    return markup


def book_inline(bron=False):
    markup = InlineKeyboardMarkup()
    if bron:
        markup.row(InlineKeyboardButton("Bron qilish☑️", callback_data="book_now"))
        return markup
    else:
        markup.row(InlineKeyboardButton("Bron qilish☑️", callback_data="book_now"),
                   InlineKeyboardButton("Lakatsiyani ko'rish📍", callback_data="send_location"))
        return markup


def yes_no_inline():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Ha✅", callback_data="proceed|1"),
               InlineKeyboardButton("Yo'q❌", callback_data="proceed|0"))
    return markup


def stadiums_choose(stadiums):
    markup = InlineKeyboardMarkup(row_width=2)
    for stadium in stadiums:
        markup.add(InlineKeyboardButton(stadium[0], callback_data=f"stadium|{stadium[1]}"))
    return markup


def booked_stadiums_choose(stadiums):
    """:return: inline btn with calldata 'book|{stadium_id}'"""
    markup = InlineKeyboardMarkup(row_width=2)
    for stadium in stadiums:
        markup.add(InlineKeyboardButton(stadium[0], callback_data=f"book|{stadium[1]}"))
    return markup
