import logging
from telebot.types import Message

from database import Session
from database.db_utils import fetch_stadium_with_owner_id
from handlers.superusers import admin_menu_markup
from loader import bot, stadium_sts, manage_sts, admin_sts, admin_menu_sts
from handlers.superusers.markups import your_stadiums_markup, yes_no_inline, main_menu_markup, regions_inline, back, \
    stadiums_choose
from utils import log_level, add_stadium_text

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="🔙Bosh sahifa", state="*", user_type="is_admin")
async def admin_back_to_main(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await bot.send_message(chat_id, "Bosh sahifa:", reply_markup=main_menu_markup())
    await bot.set_state(user_id, admin_sts.main, chat_id)


@bot.message_handler(regexp="🔙Orqaga", state="*", user_type="is_admin")
async def admin_back(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    state = await bot.get_state(user_id, chat_id)
    logger.debug(state)
    if state == "SuperUserState:region":
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
        await bot.set_state(user_id, admin_sts.main, chat_id)
    elif state in ["StadiumState:proceed", "ManageStadiums:choose_stadium"]:
        await bot.send_message(chat_id, "Stadionlar", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, stadium_sts.init)
    elif state.split(":")[0] == "StadiumState" and state.split(":")[1] in ["name", "description", "image", "price",
                                                                           "open_time", "close_time", "region",
                                                                           "district", "location"]:
        text = add_stadium_text
        await bot.send_message(chat_id, text, reply_markup=back(), parse_mode="html")
        await bot.send_message(chat_id, "Davom ettirasizmi?", reply_markup=yes_no_inline())
        await bot.set_state(user_id, stadium_sts.proceed, chat_id)
    elif state.split(":")[0] == "SuperUserState" and state.split(":")[1] in ["district", "start_time", "date", "hour"]:
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, admin_sts.region, chat_id)
    elif state == "ManageStadiums:edit":
        async with bot.retrieve_data(user_id, chat_id) as data:
            stadiums, msg = await fetch_stadium_with_owner_id(data["user_id"], Session)
            if stadiums:
                markup = stadiums_choose(stadiums)
                await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)
                await bot.send_message(chat_id, msg, reply_markup=markup)
    elif state == "ManageStadiums:update_attr":
        async with bot.retrieve_data(user_id, chat_id) as data:
            smi = data["manage"]["sent_message_id"]
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, smi)
        await bot.set_state(user_id, manage_sts.edit, chat_id)
    elif state.split(":")[0] == "AdminMenu" and state.split(":")[1] in ["data", "get_user", "get_admin"]:
        await bot.send_message(chat_id, "Admin menu:", reply_markup=admin_menu_markup(user_id))
        await bot.set_state(user_id, admin_menu_sts.main, chat_id)
    else:
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
        await bot.set_state(user_id, admin_sts.main, chat_id)
