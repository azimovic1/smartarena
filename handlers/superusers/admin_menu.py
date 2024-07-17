import os
import logging
from telebot.types import Message

from database.db_utils import add_owner_to_db, add_admin_to_db
from loader import bot, admin_sts, admin_menu_sts
from database import Session
from utils import log_level
from .markups.buttons import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@bot.message_handler(regexp="👨‍💻Admin", user_type="is_admin", state=admin_sts.main)
async def admin_menu_(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Admin menu:", reply_markup=admin_menu_markup(user_id))
    await bot.set_state(user_id, admin_menu_sts.main, chat_id)


@bot.message_handler(regexp="Bot ma'lumotlari📖", user_type="is_admin", state=admin_menu_sts.main)
async def admin_menu_datas(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '../../'))
    db_path = os.path.join(project_root, 'database', 'db.sqlite3')
    with open(db_path, 'rb') as file:
        await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
        await bot.send_document(chat_id, file, reply_markup=main_menu_markup())
    await bot.set_state(user_id, admin_sts.main, chat_id)


@bot.message_handler(regexp="Owner qo'shish🕵️‍♂️", user_type="is_admin", state=admin_menu_sts.main)
async def admin_add_owners(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = get_user_from_chat(message.message_id)
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, "Userni tanlang🕵️‍♂️ yoki user telefon raqamini kiriting☎️", reply_markup=markup)
    await bot.set_state(user_id, admin_menu_sts.get_user, chat_id)


@bot.message_handler(content_types=["users_shared"], user_type="is_admin", state=admin_menu_sts.get_user)
async def admin_get_owners_id(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    owner_id = message.users_shared.user_ids
    await bot.send_chat_action(chat_id, "TYPING")
    success, result = await add_owner_to_db(owner_id, Session)
    if success is None:
        await bot.send_message(chat_id, result, reply_markup=get_user_from_chat(message.message_id))
        await bot.set_state(user_id, admin_menu_sts.get_user, chat_id)
    elif success:
        await bot.send_message(chat_id, result, reply_markup=admin_menu_markup(user_id))
        await bot.set_state(user_id, admin_menu_sts.main, chat_id)
    else:
        await bot.send_message(chat_id, result,
                               reply_markup=main_menu_markup())
        await bot.set_state(user_id, admin_sts.main)


@bot.message_handler(state=admin_menu_sts.get_user, content_types=["text"], user_type="is_admin",
                     func=lambda msg: msg.text not in ("🔙Orqaga", "🔙Bosh sahifa"))
async def admin_add_owners_number(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    success, result = await add_owner_to_db(message.text, Session, number=True)
    if success is None:
        await bot.send_message(chat_id, result,
                               parse_mode="html", reply_markup=())
    elif success:
        await bot.send_message(chat_id, result, reply_markup=admin_menu_markup(user_id))
        await bot.set_state(user_id, admin_menu_sts.main, chat_id)
    else:
        await bot.send_message(chat_id, result,
                               reply_markup=get_user_from_chat(message.message_id))
        await bot.set_state(user_id, admin_sts.main)


@bot.message_handler(regexp="Admin qo'shish👨‍💻", user_type="is_admin", state=admin_menu_sts.main)
async def admin_add_admin(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = get_user_from_chat(message.message_id)
    await bot.send_chat_action(chat_id, "TYPING")
    await bot.send_message(chat_id, "Userni tanlang🕵️‍♂️ yoki user telefon raqamini kiriting☎️", reply_markup=markup)
    await bot.set_state(user_id, admin_menu_sts.get_admin, chat_id)


@bot.message_handler(content_types=["users_shared"], user_type="is_admin", state=admin_menu_sts.get_admin)
async def admin_add_admins_id(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    owner_id = message.users_shared.user_ids
    await bot.send_chat_action(chat_id, "TYPING")
    success, result = await add_admin_to_db(owner_id, Session)
    if success is None:
        await bot.send_message(chat_id, result, reply_markup=get_user_from_chat(message.message_id))
        await bot.set_state(user_id, admin_menu_sts.get_user, chat_id)
    elif success:
        await bot.send_message(chat_id, result, reply_markup=admin_menu_markup(user_id))
        await bot.set_state(user_id, admin_menu_sts.main, chat_id)
    else:
        await bot.send_message(chat_id, result,
                               reply_markup=main_menu_markup())
        await bot.set_state(user_id, admin_sts.main)


@bot.message_handler(state=admin_menu_sts.get_admin, content_types=["text"], user_type="is_admin",
                     func=lambda msg: msg.text not in ("🔙Orqaga", "🔙Bosh sahifa"))
async def admin_add_admins_number(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    success, result = await add_admin_to_db(message.text, Session, number=True)
    if success is None:
        await bot.send_message(chat_id, result,
                               parse_mode="html", reply_markup=())
    elif success:
        await bot.send_message(chat_id, result, reply_markup=admin_menu_markup(user_id))
        await bot.set_state(user_id, admin_menu_sts.main, chat_id)
    else:
        await bot.send_message(chat_id, result,
                               reply_markup=get_user_from_chat(message.message_id))
        await bot.set_state(user_id, admin_sts.main)
