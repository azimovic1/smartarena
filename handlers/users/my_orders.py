from telebot.types import Message
from loader import bot, user_sts
from database import Session
from database.db_utils import retrieve_upcoming_orders
from handlers.users.markups.buttons import view_bookings_markup


@bot.message_handler(user_type="is_user", regexp="📅 Buyurtmalarni Ko'rish", state=user_sts.main)
async def my_booking_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, "Buyurtmalarni ko'rish:", reply_markup=view_bookings_markup())
    await bot.set_state(user_id, user_sts.bookings, chat_id)


@bot.message_handler(user_type="is_user",
                     func=lambda msg: msg.text in ["📆 Buyurtmalar tarixi", "🔜 Kelayotgan buyurtmalar"],
                     state=user_sts.bookings)
async def upcoming_history_bookings(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        text = await retrieve_upcoming_orders(data, conn=Session, msg=message.text)
    if text == "":
        await bot.send_message(chat_id, "Buyurtmalar yo'q")
    else:
        await bot.send_message(chat_id, text, parse_mode="html", reply_markup=view_bookings_markup())
    await bot.set_state(user_id, user_sts.bookings, chat_id)
