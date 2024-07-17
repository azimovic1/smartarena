from telebot.asyncio_handler_backends import ContinueHandling
from telebot.types import Message, CallbackQuery
import logging

from loader import bot, user_sts  # log_level
from database import Session
from handlers.users.markups.buttons import *
from handlers.users.markups.inline_buttons import *
from utils import log_level, regions_file_path
from database.db_utils import get_filtered_stadiums, add_order_to_db, stadium_preview_get_text_image, \
    get_ordered_stadiums

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(state=user_sts.main, regexp="📆Bron qilish")
async def book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")

    async with bot.retrieve_data(user_id, chat_id) as data:
        there_is_booked_st = data.get("last_booked_stadiums", False)

        if there_is_booked_st is False:
            await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
            await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
            await bot.set_state(user_id, user_sts.region, chat_id)
        else:
            region = data.get("region")
            district = data.get("district")
            stadiums = await get_ordered_stadiums(user_id, region, district, Session)
            data["last_booked_stadiums"].extend(stadiums)
            data["last_booked_stadiums"] = list(set(data["last_booked_stadiums"]))
            await bot.send_message(chat_id, "Bron qilish", reply_markup=quickbook_simplebook())


@bot.message_handler(state=user_sts.main, func=lambda msg: msg.text in ["Bron qilish📆", "Oldingi bronlar📆"])
async def quick_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    if message.text == "Oldingi bronlar📆":
        async with bot.retrieve_data(user_id, chat_id) as data:
            markup = booked_stadiums_choose(data["last_booked_stadiums"])
        await bot.send_message(chat_id, "Bronlar", reply_markup=back())
        await bot.send_message(chat_id, "Stadionni tanlang!", reply_markup=markup)
        await bot.set_state(user_id, user_sts.re_book, chat_id)
    else:
        await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, user_sts.region, chat_id)


@bot.callback_query_handler(state=user_sts.re_book, func=lambda call: "book" in call.data.split("|"))
async def rebook_get_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    stadium_id = int(call.data.split("|")[1])
    markup = date_time()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_id"] = stadium_id
        data["rebook"] = True
    await bot.set_state(user_id, user_sts.date, chat_id)
    await bot.edit_message_text("Sanani Tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(state=user_sts.region, func=lambda call: "region" in call.data.split('|'))
async def region_choose(call: CallbackQuery):
    # calldata: region|{region_id}

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    region_id = int(call.data.split("|")[1])
    markup = district_inline(region_id)
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.answer_callback_query(call.id, "Tumanni tanlang")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["region"] = region_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]
        data["region_name"] = region['name']

    sent = await bot.send_message(chat_id, f"{region['name']}")

    await bot.delete_message(chat_id, sent.message_id)
    await bot.set_state(user_id, user_sts.district, chat_id)
    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(state=user_sts.district, func=lambda call: "district" in call.data.split('|'))
async def district_choose(call: CallbackQuery):
    # district|{district_id}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    markup = date_time()
    await bot.answer_callback_query(call.id, "Sanani tanlang")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["district"] = district_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            data["district_name"] = district['name']
    await bot.set_state(user_id, user_sts.date, chat_id)
    await bot.edit_message_text("Sanani Tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(state=user_sts.date, func=lambda call: "date" in call.data.split("|"))
async def date_choose(call: CallbackQuery):
    # date | {date.strftime('%Y:%m:%d')}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    date = call.data.split("|")[1]
    markup = start_time_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["date"] = date
    await bot.set_state(user_id, user_sts.start_time, chat_id)
    await bot.answer_callback_query(call.id, "Vaqtini tanlang")
    await bot.edit_message_text("Boshlash vaqti", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(state=user_sts.start_time, func=lambda call: "start_time" in call.data.split('|'))
async def start_time_choose(call: CallbackQuery):
    # start_time | {time}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    start_time = call.data.split("|")[1]
    markup = hours_inline()

    async with bot.retrieve_data(user_id, chat_id) as data:
        data["start_time"] = start_time
    await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)
    await bot.set_state(user_id, user_sts.hour, chat_id)
    await bot.answer_callback_query(call.id, "Necha Soat")


@bot.callback_query_handler(state=user_sts.hour, func=lambda call: "hour" in call.data, user_type="is_user")
async def hour_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    hour = int(call.data.split("|")[1])
    await bot.answer_callback_query(call.id, "Stadionlar")

    try:
        async with bot.retrieve_data(user_id, chat_id) as data:
            rebook = data.pop("rebook", False)
            stadium_id = data.get("stadium_id")
            data["hour"] = hour
            region_filter = data["region_name"]
            district_filter = data["district_name"]
            start_time_str = data["start_time"]
            date_str = data["date"]
            date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
            start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
            hour_filter = data["hour"]
            markup = main_menu_markup()
            stadiums = await get_filtered_stadiums(Session, region_filter, district_filter, combined_datetime,
                                                   hour_filter, stadium_id)

            if stadiums is None or len(stadiums) < 1:
                await bot.set_state(user_id, user_sts.main, chat_id)
                await bot.send_message(chat_id, "Berilgan filterlar boyicha stadionlar mavjud emas yoki Band!",
                                       reply_markup=markup)
            else:
                if rebook:
                    call.data = f"book|{stadium_id}"
                    await stadium_preview(call)
                    return ContinueHandling()
                else:
                    await bot.send_message(chat_id, "Stadionlar", reply_markup=markup)
                    await bot.send_message(chat_id, "Tanlang", reply_markup=stadiums_inline(stadiums))
                await bot.set_state(user_id, user_sts.main, chat_id)
    except Exception as e:
        logger.error(f"error occured {e}", exc_info=True)


@bot.callback_query_handler(state=user_sts.main, func=lambda call: "book" in call.data.split("|"))
async def stadium_preview(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as bdata:
        bdata["stadium_id"] = data
        message, images, name = await stadium_preview_get_text_image(data, bdata, Session)
        bdata["stadium_name"] = name
        # await bot.set_state(user_id, user_sts.loc_book, chat_id)
        try:
            await bot.send_media_group(chat_id, images)
        except Exception as e:
            logger.warning(f"stadium {data} has no images {e}")
        await bot.send_message(chat_id, message, parse_mode="html", reply_markup=book_inline())
        await bot.answer_callback_query(call.id, f"stadion {name}")


@bot.callback_query_handler(state=user_sts.main, user_type="is_user",
                            func=lambda call: call.data in ["book_now", "send_location"])
async def location_book(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    if data == "book_now":
        # format_string = "%Y-%m-%d %H:%M:%S"
        async with bot.retrieve_data(user_id, chat_id) as data:
            last_book_check = data.get("last_booked_stadiums", False)
            if last_book_check:
                if (data["stadium_name"], data["stadium_id"]) not in data["last_booked_stadiums"]:
                    data["last_booked_stadiums"].append((data["stadium_name"], data["stadium_id"]))
            else:
                data["last_booked_stadiums"] = [(data["stadium_name"], data["stadium_id"])]

            text = await add_order_to_db(data, Session)
            del data["region"], data["region_name"], data["district"], data["district_name"], data["stadium_id"], data[
                "location"], data["stadium_name"]

        await bot.answer_callback_query(call.id, f"Bajarildi✅")
        await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
        await bot.send_message(-1002049070221, text, parse_mode="html")
        await bot.set_state(user_id, user_sts.main, chat_id)

    else:
        await bot.answer_callback_query(call.id, f"Lokatsiya")
        async with bot.retrieve_data(user_id, chat_id) as bdata:
            location = bdata.get("location")
        await bot.send_location(chat_id, **location, reply_markup=book_inline(True))


