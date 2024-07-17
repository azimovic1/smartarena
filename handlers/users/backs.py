from telebot.types import Message
from loader import bot, user_sts
from utils.config import log_level
from .markups.buttons import *
import logging

from .markups import regions_inline

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="🔙Bosh sahifa", state="*", user_type="is_user")
async def back_to_main(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Bosh sahifa:", reply_markup=main_menu_markup())
    await bot.set_state(user_id, user_sts.main, chat_id)


@bot.message_handler(regexp="🔙Orqaga", state="*", user_type="is_user")
async def back(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    state = await bot.get_state(user_id, chat_id)
    logger.debug(state)
    if state == "UserState:region":
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
        await bot.set_state(user_id, user_sts.main, chat_id)
    elif state.split(":")[1] in ["district", "start_time", "date", "hour"]:
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, user_sts.region, chat_id)
    else:
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
        await bot.set_state(user_id, user_sts.main, chat_id)
