import logging
from telebot.types import Message

from loader import bot, auth_sts, user_sts
from utils import log_level
from database.db_utils import user_check
from .markups.buttons import login_signup, main_menu_markup
from database import Session

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(user_type="is_user", commands=["start"], chat_types=["private"])
async def greeting(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = await user_check(user_id, Session)

    if user:
        await bot.send_message(chat_id, f"Salom {user.username}", reply_markup=main_menu_markup())
        await bot.set_state(user_id, user_sts.main, chat_id)
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["user_id"] = user.id
    else:
        await bot.send_message(chat_id, f"Salom {message.from_user.first_name}",
                               reply_to_message_id=message.message_id,
                               reply_markup=login_signup())
        await bot.set_state(user_id, auth_sts.init, chat_id)
