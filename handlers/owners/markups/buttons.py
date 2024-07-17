from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def view_bookings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔜 Kelayotgan buyurtmalar"), KeyboardButton("📆 Buyurtmalar tarixi"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def quickbook_simplebook():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Bron qilish📆"), KeyboardButton("Oldingi bronlar📆"))
    return markup


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🏟️Stadionlarim"), KeyboardButton("📆Bron qilish"))
    markup.row(KeyboardButton("📅 Buyurtmalarni Ko'rish"), KeyboardButton("ℹ️Yordam"))
    return markup


def your_stadiums_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🌐Stadion qo'shish"), KeyboardButton("🛠️Stadionlarimni boshqarish"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup


def done():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Jo'natib bo'ldim👌"))
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup


def request_location():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Lokatsiyani jo'natish🗺📍", request_location=True))
    markup.row(KeyboardButton("Keyingisi⏭"))
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup
