import logging
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery

from loader import bot, auth_sts, user_sts, log_level
from utils import register_confirmation, register_success
from database.db_utils import add_new_user, check_phone_number
from .markups import confirmation
from .markups.buttons import *
from database.connection import Session

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="Ro'yxatdan o'tish🗒", state=auth_sts.init)
async def signup_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, "Ism Familyangizni yuboring.", reply_to_message_id=message.message_id,
                           reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, auth_sts.name, chat_id)
    return


@bot.message_handler(content_types=["text"], state=auth_sts.name)
async def name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["user_data"] = {}
        data["user_data"]["telegram_id"] = user_id
        data["user_data"]["username"] = message.text

    await bot.send_message(chat_id, "Telefon raqamingizni yuboring", reply_to_message_id=message.message_id,
                           reply_markup=number_request())
    await bot.set_state(user_id, auth_sts.number, chat_id)


@bot.message_handler(content_types=["text", "contact"], state=auth_sts.number)
async def number_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    number = message.text if message.content_type == "text" else message.contact.phone_number
    number = f"+{number}" if "+" not in number else number
    check = await check_phone_number(number, Session)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["user_data"]["number"] = number
        name = data["user_data"]["username"]
        text = register_confirmation(name, number, check)
    if check:
        await bot.send_message(chat_id, "<b>Malumotni Tasdiqlang:</b>", parse_mode="html",
                               reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id, text, reply_markup=confirmation(), parse_mode="html")
        await bot.set_state(user_id, auth_sts.confirm, chat_id)
    else:
        await bot.send_message(chat_id, text, parse_mode="html", reply_to_message_id=message.message_id)


@bot.callback_query_handler(state=auth_sts.confirm,func=lambda call: call.data.split("|")[0] == "confirm")
async def confirmation_inline(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    markup = login_signup()
    operation_success = True
    is_confirmed = int(callback.data.split("|")[1])  # 1/0
    if is_confirmed:
        async with bot.retrieve_data(user_id, chat_id) as data:
            user_data = data["user_data"]
            new_user = await add_new_user(user_data, Session)
            if new_user:
                data["user_id"] = new_user.id
                operation_success = True
                markup = main_menu_markup()
                await bot.set_state(user_id, user_sts.main, chat_id)
            else:
                operation_success = False
                await bot.set_state(user_id, auth_sts.init, chat_id)
            text = register_success(**user_data, check=operation_success, is_confirmed=is_confirmed)
    else:
        markup = None
        text = register_success(check=operation_success, is_confirmed=is_confirmed)
        await bot.set_state(user_id, auth_sts.name, chat_id)
    await bot.answer_callback_query(callback.id, text[1])
    await bot.send_message(chat_id, text=text[0], parse_mode="html", reply_markup=markup)
