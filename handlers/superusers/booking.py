import logging

from telebot.asyncio_handler_backends import ContinueHandling
from telebot.types import CallbackQuery, Message

from loader import bot, admin_sts
from database import Session
from handlers.superusers.markups.buttons import *
from handlers.superusers.markups.inline_buttons import *
from utils import log_level, regions_file_path
from database.db_utils import get_filtered_stadiums, add_order_to_db, stadium_preview_get_text_image, \
    get_ordered_stadiums

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="📆Bron qilish", state=admin_sts.main)
async def admin_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")

    async with bot.retrieve_data(user_id, chat_id) as data:
        there_is_booked_st = data.get("last_booked_stadiums", False)
        logger.info(f"admin book, admin_sts.main| booked stadium{there_is_booked_st} ")

    if there_is_booked_st is False:
        await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, admin_sts.region, chat_id)
    else:
        region = data.get("region")
        district = data.get("district")
        stadiums = await get_ordered_stadiums(user_id, region, district, Session)
        data["last_booked_stadiums"].extend(stadiums)
        data["last_booked_stadiums"] = list(set(data["last_booked_stadiums"]))
        await bot.send_message(chat_id, "Bron qilish", reply_markup=quickbook_simplebook())


@bot.message_handler(func=lambda msg: msg.text in ["Bron qilish📆", "Oldingi bronlar📆"], state=admin_sts.main)
async def admin_quick_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    if message.text == "Oldingi bronlar📆":
        logger.info(f"admin_sts.main quickbook {message.text}")
        async with bot.retrieve_data(user_id, chat_id) as data:
            markup = booked_stadiums_choose(data["last_booked_stadiums"])
        await bot.send_message(chat_id, "Bronlar", reply_markup=back())
        await bot.send_message(chat_id, "Stadionni tanlang!", reply_markup=markup)
        await bot.set_state(user_id, admin_sts.re_book, chat_id)
    else:
        await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, admin_sts.region, chat_id)


@bot.callback_query_handler(state=admin_sts.re_book, func=lambda call: "ad_book" in call.data.split("|"))
async def admin_rebook_get_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    markup = date_time()
    logger.info(f"admin_sts.re_book {call.data}")
    async with bot.retrieve_data(user_id, chat_id) as bdata:
        bdata["stadium_id"] = data
        bdata["rebook"] = True
    await bot.set_state(user_id, admin_sts.date, chat_id)
    await bot.edit_message_text("Sanani Tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "adreg" in call.data.split('|'), state=admin_sts.region)
async def admin_region_choose(call: CallbackQuery):
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
            logger.info(f"admin_sts.region book region {region}")
        data["region_name"] = region['name']

    sent = await bot.send_message(chat_id, f"{region['name']}")

    await bot.delete_message(chat_id, sent.message_id)
    await bot.set_state(user_id, admin_sts.district, chat_id)
    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "addist" in call.data.split('|'), state=admin_sts.district)
async def admin_district_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    markup = date_time()
    await bot.answer_callback_query(call.id, "Sanani tanlang")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["district"] = district_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            logger.info(f"admin_sts.district book district {district}")
            data["district_name"] = district['name']

    await bot.set_state(user_id, admin_sts.date, chat_id)
    await bot.edit_message_text("Sanani Tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(state=admin_sts.date, func=lambda call: "addate" in call.data.split("|"))
async def admin_date_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    date = call.data.split("|")[1]
    markup = start_time_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["date"] = date
        logger.info(f"admin_sts.date book date {date}")

    await bot.set_state(user_id, admin_sts.start_time, chat_id)
    await bot.answer_callback_query(call.id, "Vaqtini tanlang")
    await bot.edit_message_text("Boshlash vaqti", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "ads_time" in call.data.split('|'), state=admin_sts.start_time)
async def admin_start_time_choose(call: CallbackQuery):
    # start_time | {time}
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    start_time = call.data.split("|")[1]
    markup = hours_inline()
    logger.info(f"admin_sts.start_time book start_time {start_time}")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["start_time"] = start_time
    await bot.set_state(user_id, admin_sts.hour, chat_id)
    await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)
    await bot.answer_callback_query(call.id, "Necha Soat")


@bot.callback_query_handler(state=admin_sts.hour, func=lambda call: "adhour" in call.data.split('|'),
                            user_type="is_admin")
async def admin_hour_choose(call: CallbackQuery):
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
            logger.info(f"admin_sts.hour book hour{hour} No St{len(stadiums)}")

            if stadiums is None or len(stadiums) < 1:
                await bot.set_state(user_id, admin_sts.main, chat_id)
                await bot.send_message(chat_id, "Berilgan filterlar boyicha stadionlar mavjud emas yoki Band!",
                                       reply_markup=markup)
            else:
                if rebook:
                    logger.info(f"admin_sts.hour book rebook {hour, len(stadiums)} continue handling preview")
                    call.data = f"adbook|{stadium_id}"
                    await admin_stadium_preview(call)
                else:
                    await bot.send_message(chat_id, "Stadionlar", reply_markup=markup)
                    await bot.send_message(chat_id, "Tanlang", reply_markup=stadiums_inline(stadiums))

                await bot.set_state(user_id, admin_sts.main, chat_id)
    except Exception as e:
        logger.error(f"error occured {e}", exc_info=True)


@bot.callback_query_handler(state=admin_sts.main, func=lambda call: "adbook" in call.data.split("|"))
async def admin_stadium_preview(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as bdata:
        bdata["stadium_id"] = data
        message, images, name = await stadium_preview_get_text_image(data, bdata, Session)
        bdata["stadium_name"] = name
        logger.info(f"admin_sts.preview book: {name}, {len(images)} images")

        # await bot.set_state(user_id, admin_sts.loc_book, chat_id)
        try:
            await bot.send_media_group(chat_id, images)
        except Exception as e:
            logger.warning(f"stadium {data} has no images {e}")
        await bot.send_message(chat_id, message, parse_mode="html", reply_markup=book_inline())
        await bot.answer_callback_query(call.id, f"stadion {name}")


@bot.callback_query_handler(func=lambda call: call.data in ["adbook_now", "adsend_loc"], user_type="is_admin",
                            state=admin_sts.main)
async def admin_location_book(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    logger.info(f"admin_sts.loc_book book {data}")
    if data == "adbook_now":
        # format_string = "%Y-%m-%d %H:%M:%S"
        async with bot.retrieve_data(user_id, chat_id) as data:
            last_book_check = data.get("last_booked_stadiums", False)
            if last_book_check:
                if (data["stadium_name"], data["stadium_id"]) not in data["last_booked_stadiums"]:
                    data["last_booked_stadiums"].append((data["stadium_name"], data["stadium_id"]))
            else:
                data["last_booked_stadiums"] = [(data["stadium_name"], data["stadium_id"])]

            text = await add_order_to_db(data, Session)
            logger.info(data)

        await bot.answer_callback_query(call.id, f"Bajarildi✅")
        await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
        await bot.send_message(-1002049070221, text, parse_mode="html")
        await bot.set_state(user_id, admin_sts.main, chat_id)

    else:
        await bot.answer_callback_query(call.id, f"Lokatsiya")
        async with bot.retrieve_data(user_id, chat_id) as bdata:
            location = bdata.get("location")
        await bot.send_location(chat_id, **location, reply_markup=book_inline(True))
