import logging

from telebot.asyncio_handler_backends import ContinueHandling
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery

from database.db_utils import add_stadium_to_database
from loader import bot, stadium_sts, owner_sts
from database import Session
from handlers.owners.markups.buttons import *
from handlers.owners.markups.inline_buttons import *
from utils import add_stadium_text, get_stadium_data_text, log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(chat_types=["private"], regexp="🏟️Stadionlarim", user_type="is_owner")
async def my_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, "Stadionlar", reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, stadium_sts.init, chat_id)
    return


@bot.message_handler(chat_types=["private"], regexp="🌐Stadion qo'shish", state=stadium_sts.init, user_type="is_owner")
async def add_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = add_stadium_text
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, text, reply_markup=back(), parse_mode="html")
    await bot.send_message(chat_id, "Davom ettirasizmi?", reply_markup=yes_no_inline())
    await bot.set_state(user_id, stadium_sts.proceed, chat_id)
    return


@bot.callback_query_handler(user_type="is_owner",
                            state=stadium_sts.proceed,
                            func=lambda call: "proceed" in call.data.split("|"))
async def proceed_yes_no(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    answer = int(call.data.split("|")[1])
    await bot.send_chat_action(chat_id, "TYPING")
    if answer:
        await bot.answer_callback_query(call.id, "Malumotlarni kiritishda hushyor bo'lishingizni so'rab qolamiz❗️",
                                        show_alert=True)
        await bot.set_state(user_id, stadium_sts.name, chat_id)
        await bot.send_message(chat_id, "Stadion uchun nom kiriting")
    else:
        await bot.set_state(user_id, owner_sts.main, chat_id)
        await bot.answer_callback_query(call.id, "Bekor qilindi")
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
    return


@bot.message_handler(chat_types=["private"], content_types=["text"], state=stadium_sts.name, user_type="is_owner")
async def stadium_name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if message.text not in ["🔙Orqaga", "🔙Bosh sahifa"]:
        await bot.send_chat_action(chat_id, "TYPING")
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["stadium"] = dict()
            data["stadium"]["stadium_name"] = message.text
        await bot.set_state(user_id, stadium_sts.description, chat_id)
        await bot.send_message(chat_id, "Stadion va qo'shimcha kontakt malumotlarini matin shaklida jo'nating")
        return
    return ContinueHandling()


@bot.message_handler(chat_types=["private"], content_types=["text"], state=stadium_sts.description,
                     user_type="is_owner")
async def stadium_desc_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if message.text not in ["🔙Orqaga", "🔙Bosh sahifa"]:
        await bot.send_chat_action(chat_id, "TYPING")
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["stadium"]["stadium_description"] = message.text
            data["stadium"]["photo"] = 0
            data["stadium"]["stadium_photo"] = []
        await bot.set_state(user_id, stadium_sts.image, chat_id)
        await bot.send_message(chat_id, "Stadion uchun rasmlarni jo'nating va tugmani bosing", reply_markup=done())
        return
    return ContinueHandling()


@bot.message_handler(chat_types=["private"], content_types=["photo", "text"], state=stadium_sts.image,
                     user_type="is_owner")
async def stadium_image_handler(message: Message):
    if message.text not in ["🔙Orqaga", "🔙Bosh sahifa"]:
        chat_id = message.chat.id
        user_id = message.from_user.id
        if message.content_type == "photo":
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["stadium"]["stadium_photo"].append(message.json["photo"][-1]["file_id"])
            return
        elif message.content_type == "text" and message.text == "Jo'natib bo'ldim👌":
            async with bot.retrieve_data(user_id, chat_id) as data:
                if len(data["stadium"]["stadium_photo"]) == 0:
                    data["stadium"]["stadium_photo"].append(
                        "AgACAgIAAxkBAAIvImYv0rn-e1rv6zZxbkNVX9BKP_hSAAJw3TEbf6aASQhC2Ec6uUajAQADAgADbQADNAQ")
            await bot.send_chat_action(chat_id, "TYPING")
            await bot.send_message(chat_id, "Stadion narxini yuboring (so'm/soat)", reply_markup=back())
            await bot.set_state(user_id, stadium_sts.price, chat_id)
        return
    return ContinueHandling()


@bot.message_handler(chat_types=["private"], content_types=["text"], state=stadium_sts.price, user_type="is_owner")
async def stadium_price_handler(message: Message):
    if message.text not in ["🔙Orqaga", "🔙Bosh sahifa"]:
        chat_id = message.chat.id
        user_id = message.from_user.id
        await bot.send_chat_action(chat_id, "TYPING")
        if message.text.isdigit():
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["stadium"]["stadium_price"] = message.text
            await bot.send_message(chat_id, "Stadioning ochilish vaqti🕒", reply_markup=start_time_inline())
            await bot.set_state(user_id, stadium_sts.open_time, chat_id)
            return
        else:
            await bot.send_message(chat_id,
                                   "Stadion narxini hato formatda berdingiz❗️\nto'gri format: 000000, qaytadan kiriting (so'm/soat)")
    return ContinueHandling()


@bot.callback_query_handler(state=stadium_sts.open_time,
                            func=lambda call: "ows_time" in call.data.split("|"),
                            user_type="is_owner")
async def stadium_open_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium"]["stadium_open_time"] = call.data.split("|")[1]
        await bot.answer_callback_query(call.id, f"Ochilish vaqti: {call.data.split('|')[1]}")
        await bot.edit_message_text("Stadionning Yopilish Vaqti🕟:", chat_id, call.message.message_id,
                                    reply_markup=start_time_inline())
        await bot.set_state(user_id, stadium_sts.close_time, chat_id)
    return


@bot.callback_query_handler(state=stadium_sts.close_time, func=lambda call: "ows_time" in call.data.split("|"),
                            user_type="is_owner")
async def stadium_close_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium"]["stadium_close_time"] = call.data.split("|")[1]
        await bot.answer_callback_query(call.id, f"Yopilish vaqti: {call.data.split('|')[1]}")
        await bot.edit_message_text("Stadion joylashgan Viloyat", chat_id, call.message.message_id,
                                    reply_markup=regions_inline(1))
        await bot.set_state(user_id, stadium_sts.region, chat_id)
    return


@bot.callback_query_handler(state=stadium_sts.region, func=lambda call: "owad_reg" in call.data.split('|'),
                            user_type="is_owner")
async def stadium_region_handler(call: CallbackQuery):
    from utils.config import regions_file_path
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    region_id = int(call.data.split("|")[1])
    markup = district_inline(region_id, 1)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium"]["stadium_region"] = region_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]
        data["stadium"]["region_name"] = region['name']
        await bot.answer_callback_query(call.id, region["name"])

    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)
    await bot.set_state(user_id, stadium_sts.district, chat_id)
    return


@bot.callback_query_handler(state=stadium_sts.district, func=lambda call: "owad_dist" in call.data.split('|'),
                            user_type="is_owner")
async def district_choose(call: CallbackQuery):
    from utils.config import regions_file_path

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium"]["stadium_district"] = district_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            data["stadium"]["district_name"] = district['name']
            await bot.answer_callback_query(call.id, district["name"])
    await bot.send_message(chat_id, "Stadion joylashux nuqtasini(lokatsya) jo'nating", reply_markup=request_location())
    await bot.set_state(user_id, stadium_sts.location, chat_id)
    return


@bot.message_handler(content_types=["location", "text"], state=stadium_sts.location, user_type="is_owner",
                     chat_types=["private"])
async def stadium_location_handler(message: Message):
    if message.text not in ["🔙Orqaga", "🔙Bosh sahifa"]:
        chat_id = message.chat.id
        user_id = message.from_user.id
        await bot.send_chat_action(chat_id, "TYPING")
        async with bot.retrieve_data(user_id, chat_id) as data:
            if message.text != "Keyingisi⏭":
                data["stadium"]["location_data"] = {"longitude": message.location.longitude,
                                                    "latitude": message.location.latitude}
            else:
                data["stadium"]["location_data"] = {"longitude": 0, "latitude": 0}
        try:
            stadium_data = get_stadium_data_text(data["stadium"])
        except Exception as e:
            logger.error(f"error accured in owners/add_stadium {e}", exc_info=True)
            stadium_data = "Hatolik yuz berdi, Yordam menusidan adminga habar bering"
        await bot.send_message(chat_id, "Stadion Malumotlarini Tasdiqlang:", reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id, f"{stadium_data}",
                               reply_markup=confirmation(), parse_mode="html")
        await bot.set_state(user_id, stadium_sts.confirm, chat_id)
        return
    else:
        return ContinueHandling()


@bot.callback_query_handler(state=stadium_sts.confirm,
                            func=lambda call: call.data in ("confirm", "reject"),
                            user_type="is_owner")
async def stadium_confirmation_handler(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    if callback.data.split('|')[0] == "confirm":
        async with bot.retrieve_data(user_id, chat_id) as data:
            logger.info(f"owner.add_stadiums: line 235 :-: {data}")
            operation_success = await add_stadium_to_database(data["stadium"], data["user_id"], Session)
            data["stadium"] = dict()
        if operation_success:
            await bot.answer_callback_query(callback.id, "Tasdiqlandi✅")
            await bot.send_message(chat_id, "Stadion qo'shildi.", reply_markup=main_menu_markup())
            await bot.set_state(user_id, owner_sts.main, chat_id)
        else:
            await bot.answer_callback_query(callback.id, "Hatolik yuz berdi")
            await bot.send_message(chat_id, "Hatolik yuz berdi, qayta urinib ko'ring.",
                                   reply_markup=your_stadiums_markup())
            await bot.set_state(chat_id, stadium_sts.init, user_id)
    if callback.data.split('|')[0] == "reject":
        await bot.answer_callback_query(callback.id, "Rad etildi❌")
        await bot.send_message(chat_id, "Stadion nomini kiriting", reply_markup=back())
        await bot.set_state(user_id, stadium_sts.name, chat_id)
    return
