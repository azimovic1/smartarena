import logging

from telebot.types import Message

from loader import bot, admin_sts
from utils import log_level
from database.db_utils import user_check
from handlers.superusers.markups.buttons import main_menu_markup
from database import Session

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(user_type="is_admin", commands=["start"], chat_types=["private"])
async def greeting_admin(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    user = await user_check(user_id, Session)
    if user is False or user is None:
        logger.critical(f"error in user_type filter access by: {user_id}")
        return
    else:
        await bot.send_message(chat_id, f"Salom {user.username}", reply_markup=main_menu_markup())
        await bot.set_state(user_id, admin_sts.main, chat_id)
        async with bot.retrieve_data(user_id) as data:
            data["stadium"] = {}
            data["manage"] = {}
            data["user_id"] = user.id
