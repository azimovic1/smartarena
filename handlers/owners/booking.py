import logging

from telebot.types import CallbackQuery, Message

from loader import bot, owner_sts
from database import Session
from handlers.owners.markups.buttons import *
from handlers.owners.markups.inline_buttons import *
from utils import log_level
from database.db_utils import get_filtered_stadiums, add_order_to_db, fetch_stadium_with_owner_id

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="📆Bron qilish", state=owner_sts.main)
async def owner_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")

    async with bot.retrieve_data(user_id, chat_id) as data:
        stadiums, msg = await fetch_stadium_with_owner_id(data["user_id"], Session)

    if stadiums:
        markup = stadiums_choose(stadiums, for_booking=True)
        await bot.set_state(user_id, owner_sts.stadiums, chat_id)
        await bot.send_message(chat_id, msg, reply_markup=back())
        await bot.send_message(chat_id, "Tanlang", reply_markup=markup)
    else:
        markup = main_menu_markup()
        await bot.set_state(user_id, owner_sts.main, chat_id)
        await bot.send_message(chat_id, msg, reply_markup=markup)


@bot.callback_query_handler(state=owner_sts.stadiums, func=lambda call: "bstad" in call.data.split("|"))
async def owner_stadiums_to_book(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    stadium = call.data.split("|")[-1]
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_id"] = stadium
    await bot.set_state(user_id, owner_sts.date, chat_id)
    await bot.send_message(chat_id, "San'ani tanlang", reply_markup=date_time())
    await bot.answer_callback_query(call.id, "Sanani tanlang")


@bot.callback_query_handler(state=owner_sts.date, func=lambda call: "owdate" in call.data.split("|"))
async def owner_date_choose(call: CallbackQuery):
    # date | {date.strftime('%Y:%m:%d')}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    date = call.data.split("|")[1]
    markup = start_time_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["date"] = date
    await bot.set_state(user_id, owner_sts.start_time, chat_id)
    await bot.answer_callback_query(call.id, "Vaqtini tanlang")
    await bot.edit_message_text("Boshlash vaqti", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "ows_time" in call.data.split('|'), state=owner_sts.start_time)
async def owner_start_time_choose(call: CallbackQuery):
    # start_time | {time}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    start_time = call.data.split("|")[1]
    markup = hours_inline()

    async with bot.retrieve_data(user_id, chat_id) as data:
        data["start_time"] = start_time
    await bot.set_state(user_id, owner_sts.hour, chat_id)
    await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)
    await bot.answer_callback_query(call.id, "Necha Soat")


@bot.callback_query_handler(state=owner_sts.hour, func=lambda call: "owhour" in call.data.split('|'),
                            user_type="is_owner")
async def owner_hour_choose(call: CallbackQuery):
    # hour|1
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    hour = int(call.data.split("|")[1])
    await bot.answer_callback_query(call.id, "Stadionlar")

    try:
        async with bot.retrieve_data(user_id, chat_id) as data:
            stadium_id = data.get("stadium_id")
            data["hour"] = hour
            start_time_str = data["start_time"]
            date_str = data["date"]
            date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
            start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
            markup = main_menu_markup()
            stadiums = await get_filtered_stadiums(Session, None, None,
                                                   combined_datetime,
                                                   data["hour"], stadium_id=stadium_id)

            if stadiums is None or len(stadiums) < 1:
                await bot.send_message(chat_id, "Berilgan filterlar boyicha stadion Band!",
                                       reply_markup=markup)
            else:
                text = await add_order_to_db(data, Session)
                del data['date'], data["start_time"], data["hour"]

                await bot.answer_callback_query(call.id, f"Bajarildi✅")
                await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
                await bot.send_message(-1002049070221, text, parse_mode="html")
            await bot.set_state(user_id, owner_sts.main, chat_id)

    except Exception as e:
        logger.error(f"error occured {e}", exc_info=True)
