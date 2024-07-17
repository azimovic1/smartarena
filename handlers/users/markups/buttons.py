from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def login_signup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ro'yxatdan o'tish🗒"))
    return markup


def quickbook_simplebook():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Bron qilish📆"), KeyboardButton("Oldingi bronlar📆"))
    return markup


def number_request():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kantaktni yuborish☎️", request_contact=True))
    return markup


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📆Bron qilish"), KeyboardButton("📅 Buyurtmalarni Ko'rish"))
    markup.row(KeyboardButton("ℹ️Yordam"))
    return markup


def view_bookings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔜 Kelayotgan buyurtmalar"), KeyboardButton("📆 Buyurtmalar tarixi"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup
