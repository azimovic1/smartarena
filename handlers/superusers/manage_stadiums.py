import logging

from telebot.asyncio_handler_backends import ContinueHandling
from telebot.types import Message, CallbackQuery

from database.db_utils import fetch_stadium_with_owner_id, get_stadium_details_from_db, delete_stadium_with_id, \
    refresh_stadium_manage, get_region_id_from_db, update_stadium_fields
from loader import bot, stadium_sts, manage_sts, admin_sts
from database import Session
from handlers.superusers.markups.buttons import *
from handlers.superusers.markups.inline_buttons import *
from utils import log_level, regions_file_path, admin_check_manage_sts_edit, admin_check_all_manage_sts_edit, \
    admin_filter_update_call_handler

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(state=stadium_sts.init, regexp="🛠️Stadionlarimni boshqarish", user_type="is_admin")
async def admin_manage_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["manage"] = dict()
        stadiums, msg = await fetch_stadium_with_owner_id(data["user_id"], Session)
        logger.info(f"admin manage stadium statium_sts.init  {msg}")

        if stadiums:
            markup = stadiums_choose(stadiums)
            await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)
            await bot.send_message(chat_id, msg, reply_markup=back())
            await bot.send_message(chat_id, "Tanlang", reply_markup=markup)
        else:
            markup = your_stadiums_markup() if stadiums is None else main_menu_markup()
            await bot.set_state(user_id, stadium_sts.init, chat_id)
            await bot.send_message(chat_id, msg, reply_markup=markup)


@bot.callback_query_handler(user_type="is_admin", func=lambda call: "adstadium" in call.data.split("|"),
                            state=manage_sts.choose_stadium)
async def admin_stadium_to_manage(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    data = int(call.data.split("|")[1])
    markup = manage_stadium(data)
    images, message, location = await get_stadium_details_from_db(Session, data)
    logger.info(f"admin manage_sts.choose_stadium  {message[:20]}")

    sent_loc = await bot.send_location(chat_id, **location, reply_markup=back())
    if len(images) > 0:
        try:
            sent_me = await bot.send_media_group(chat_id, images)
        except Exception as e:
            logger.error(e)
            await bot.send_message(chat_id, "Hatolik yuz berdi admin bilan boglanib koring")
            return
    else:
        sent_me = [await bot.send_message(chat_id, "Rasmlar yo'q")]
    sent_message = await bot.send_message(chat_id, message, parse_mode="html", reply_markup=markup)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["manage"]["sent_loc"] = sent_loc.message_id
        data["manage"]["sent_media"] = [i.message_id for i in sent_me]
        data["manage"]["sent_message"] = sent_message.message_id
    await bot.set_state(user_id, manage_sts.edit, chat_id)
    await bot.answer_callback_query(call.id, "yangilash")


@bot.callback_query_handler(state=manage_sts.edit, user_type="is_admin",
                            func=lambda call: "managa" in call.data and "del" in call.data)
async def admin_delete_stadium(call: CallbackQuery):
    if call.data.split("|")[1] == "del":
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        stadium_id = int(call.data.split("|")[2])
        success, msg, call_answer = await delete_stadium_with_id(Session, stadium_id)
        logger.info(f"admin manage_sts.edit del  {success, msg}")
        await bot.answer_callback_query(call.id, call_answer)
        if success:
            async with bot.retrieve_data(user_id, chat_id) as data:
                stadiums, fetch_msg = await fetch_stadium_with_owner_id(data["user_id"], Session, no_left=True)
            if stadiums:
                markup = stadiums_choose(stadiums)
                await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)
                await bot.send_message(chat_id, fetch_msg, reply_markup=markup)
            else:
                await bot.set_state(user_id, stadium_sts.init, chat_id)
                await bot.send_message(chat_id, fetch_msg, reply_markup=your_stadiums_markup())
        await bot.delete_message(chat_id, call.message.message_id)
    return


@bot.callback_query_handler(state=manage_sts.edit, user_type="is_admin",
                            func=lambda call: "managa" in call.data and "refr" in call.data)
async def admin_owner_refresh_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    stadium_id = int(call.data.split("|")[2])
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.answer_callback_query(call.id, "Yangilanyapti")
    markup = manage_stadium(stadium_id)
    success, stadium, message, images = await refresh_stadium_manage(stadium_id, Session)
    logger.info(f"admin manage_sts.edit refr  {success, message}")
    if success:
        async with bot.retrieve_data(user_id, chat_id) as data:
            await bot.delete_message(chat_id, data["manage"]["sent_loc"])
            await bot.delete_message(chat_id, data["manage"]["sent_message"])
            for i in data["manage"]["sent_media"]:
                await bot.delete_message(chat_id, i)
            if stadium.location:
                sent_loc = await bot.send_location(chat_id, **stadium.location, reply_markup=back())
            else:
                sent_loc = await bot.send_message(chat_id, "Lakatsya yo'q")
            if len(images) > 0:
                sent_me = await bot.send_media_group(chat_id, images)
            else:
                sent_me = [await bot.send_message(chat_id, "Rasmlar yo'q")]

            sent_message = await bot.send_message(chat_id, message, parse_mode="html", reply_markup=markup)
            data["manage"]["sent_loc"] = sent_loc.message_id
            data["manage"]["sent_media"] = [i.message_id for i in sent_me]
            data["manage"]["sent_message"] = sent_message.message_id
    else:
        async with bot.retrieve_data(user_id, chat_id) as data:
            data.pop("manage")
            await bot.send_message(chat_id, message, reply_markup=your_stadiums_markup())


@bot.callback_query_handler(state=manage_sts.edit, user_type="is_admin",
                            func=admin_check_manage_sts_edit)
async def admin_owner_edit_stadium_data(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    target = call.data.split("|")[1]
    stadium_id = int(call.data.split("|")[2])
    region_id = await get_region_id_from_db(stadium_id, Session)
    logger.info(f"admin manage_sts.edit edit {stadium_id, target}")
    manage_options = {
        "name": ("Stadion uchun yangi nomni jo'nating", back(), "name"),
        "desc": ("Stadion uchun yangi ma'lumotni jo'nating", back(), "description"),
        "image": ("Yangi Rasmlarni jo'nating va tugmani bosing", done(), "image_urls"),
        "price": ("Stadion uchun yangi narxni jo'nating", back(), "price"),
        "otime": ("Ochilish vaqtini o'zgartirish", start_time_inline(), "opening_time"),
        "ctime": ("Yopilish vaqtini o'zgartirish", start_time_inline(), "closing_time"),
        "reg": ("Yangi Viloyatni tanlang", regions_inline(), "region"),
        "dist": ("Yangi Tumanni tanlang", district_inline(region_id), "district"),
        "loc": ("Yangi Lokatsiyani jo'nating", request_location(), "location")
    }

    if region_id:
        text, markup, field_name = manage_options[target]
        sent = await bot.send_message(chat_id, text, reply_markup=markup)
        await bot.set_state(user_id, manage_sts.update_attr, chat_id)
        await bot.answer_callback_query(call.id, "yangilash")
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["manage"]["edit_stadium_id"] = stadium_id
            data["manage"]["sent_message_id"] = sent.message_id
            data["manage"]["message"] = text
            data["manage"]["db_fieldname"] = field_name
            repeat_msg = data["manage"].get("result_msg")
            if repeat_msg is not None:
                await bot.delete_message(chat_id, repeat_msg)
        return
    else:
        await bot.answer_callback_query(call.id, "Hatolik yuz berdi")
        await bot.send_message(chat_id, "Hatolik yuz berdi admin bilan bog'laning")
        await bot.set_state(user_id, admin_sts.init, chat_id)
        return


@bot.callback_query_handler(state=manage_sts.update_attr, user_type="is_admin",
                            func=admin_check_all_manage_sts_edit)
async def admin_owner_edit_stadium_data(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    logger.info(f"admin manage_sts.update_attr anti callback flood {user_id, chat_id}")
    async with bot.retrieve_data(user_id, chat_id) as data:
        message = data["manage"].get("message")
        await bot.answer_callback_query(call.id, f"Birinchi {message}⚠️", show_alert=True)
    return


@bot.message_handler(state=manage_sts.update_attr, user_type="is_admin", content_types=["text", "location", "photo"],
                     func=lambda msg: msg.text not in ["🔙Orqaga", "🔙Bosh sahifa"])
async def admin_stadium_update_msg_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    value = None
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["manage"]["sent_message_id"])
        stadium_id = data["manage"]["edit_stadium_id"]
        field_name = data["manage"]["db_fieldname"]
        logger.info(f"admin manage_sts.update_attr message {field_name, stadium_id}")

    if message.content_type == "location":
        value = {"longitude": message.location.longitude, "latitude": message.location.latitude}
    elif message.content_type == "photo":
        images = data["manage"].get("images", ["AgACAgIAAxkBAAIvImYv0rn-e1rv6zZxbkNVX9BKP_hSAAJw3TEbf6aASQhC2Ec6uUajAQADAgADbQADNAQ"])
        images.append(message.json["photo"][-1]["file_id"])
        data["manage"]["images"] = images
    else:
        value = message.text
        if field_name == "price":
            if not value.isdigit():
                alert = await bot.send_message(chat_id, "Stadion narxini hato formatda berdingiz❗️\n"
                                                        "to'gri format: 000000, qaytadan kiriting (so'm/soat)")
                data["manage"]["sent_message_id"] = alert.message_id
                return ContinueHandling()
            value = message.text
        elif value == "Keyingisi⏭":
            value = {"longitude": 0, "latitude": 0}
        elif value == "Jo'natib bo'ldim👌":
            default_image = ["AgACAgIAAxkBAAIvImYv0rn-e1rv6zZxbkNVX9BKP_hSAAJw3TEbf6aASQhC2Ec6uUajAQADAgADbQADNAQ"]
            value = data["manage"].get("images", default_image)

    result = await update_stadium_fields(stadium_id, {field_name: value}, Session)
    result_msg = await bot.send_message(chat_id, result, reply_markup=back())
    data["manage"]["result_msg"] = result_msg.message_id
    await bot.set_state(user_id, manage_sts.edit, chat_id)


@bot.callback_query_handler(state=manage_sts.update_attr, user_type="is_admin",
                            func=admin_filter_update_call_handler)
async def admin_stadium_update_call_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    calldata = call.data.split("|")
    value = calldata[-1]
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["manage"]["sent_message_id"])
        stadium_id = data["manage"]["edit_stadium_id"]
        field_name = data["manage"]["db_fieldname"]
        logger.info(f"admin manage_sts.update_attr callback {field_name, stadium_id}")
        if field_name == "region":
            with open(regions_file_path, "r", encoding="utf-8") as file:
                region_id = int(value)
                value = json.load(file)["regions"][region_id - 1]["name"]
        elif field_name == "district":
            district_id = int(value)
            with open(regions_file_path, "r", encoding="utf-8") as file:
                value = json.load(file)["districts"][district_id - 15]["name"]

    result = await update_stadium_fields(stadium_id, {field_name: value}, Session)
    await bot.answer_callback_query(call.id, f"{result}🔄")
    sent = await bot.send_message(chat_id, result, reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, manage_sts.edit, chat_id)
    await bot.delete_message(chat_id, sent.message_id)
