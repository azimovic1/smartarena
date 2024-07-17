from telebot.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUsers


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("👨‍💻Admin"))
    markup.row(KeyboardButton("📆Bron qilish "), KeyboardButton("🏟️Stadionlarim"))
    markup.row(KeyboardButton("📅 Buyurtmalarni Ko'rish"))
    return markup


def admin_menu_markup(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Owner qo'shish🕵️‍♂️"), KeyboardButton("Bot ma'lumotlari📖"))
    if user_id == 1360926475:
        markup.row(KeyboardButton("Admin qo'shish👨‍💻"), KeyboardButton("🔙Bosh sahifa"))
    else:
        markup.row(KeyboardButton("🔙Bosh sahifa"))
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


def quickbook_simplebook():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Bron qilish📆"), KeyboardButton("Oldingi bronlar📆"))
    return markup


def get_user_from_chat(request_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    request_user = KeyboardButtonRequestUsers(request_id, user_is_bot=False)
    button = KeyboardButton("Userni tanlash🕵️‍♂️", request_user=request_user)
    markup.add(button)
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup


def view_bookings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔜 Kelayotgan buyurtmalar"), KeyboardButton("📆 Buyurtmalar tarixi"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup
