from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['help'])
@bot.message_handler(regexp="ℹ️Yordam")
async def help_handler(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Yordam yoki baglar uchun ogohlantirish uchun '' ga murojat qiling ")
