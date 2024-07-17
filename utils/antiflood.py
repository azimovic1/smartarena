import asyncio
import logging

from sqlalchemy import select
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate, ContinueHandling
from telebot.types import Message, CallbackQuery, BotCommand
from telebot.async_telebot import AsyncTeleBot

from database import Session, User
from loader import bot, neutral_sts
from utils import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


class UserTypeFilter(AdvancedCustomFilter):
    key = 'user_type'

    async def check(self, message, user_type):
        user_id = message.from_user.id
        chat_id = message.chat.id if not isinstance(message, CallbackQuery) else message.message.chat.id
        await asyncio.sleep(0.01)
        # checking for /start in case the user_type is just changed
        if isinstance(message, Message) and getattr(message, "text") == "/start":
            logger.info(f"start from {user_type}")
            await initialize_user_state(bot, user_id, chat_id)
            if await check_database_for_user_type(bot, user_id, chat_id, user_type):
                return True
            return user_type == "is_user"
        # others
        else:
            try:
                async with bot.retrieve_data(user_id, chat_id) as data:
                    logger.info(f"{user_type} state data {data}")
                    cached_user_type = data.get("user_type")
                    if cached_user_type == user_type:
                        return True
            except Exception as e:
                logger.warning(f"No state set for user {user_id}, attempting to initialize: {e}")
                await initialize_user_state(bot, user_id, chat_id)
                if await check_database_for_user_type(bot, user_id, chat_id, user_type):
                    return True
            return user_type == "is_user"


async def initialize_user_state(bot_, user_id, chat_id):
    await bot_.set_state(user_id, neutral_sts.init, chat_id)


async def check_database_for_user_type(bot_, user_id, chat_id, user_type):
    try:
        async with Session() as db:
            user_query = select(User).where(User.telegram_id == int(user_id))
            user = (await db.execute(user_query)).scalar_one_or_none()

            if user and getattr(user, user_type, False):
                async with bot_.retrieve_data(user_id, chat_id) as data:
                    data["user_type"] = user_type
                    data["user_id"] = user.id
                return True
        return False

    except Exception as e:
        logger.error(f"Error checking user_type for user {user_id} from the database: {e}", exc_info=True)
    return False


bot.add_custom_filter(UserTypeFilter())


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit, _bot):
        super().__init__()
        self.last_time = {}
        self.notification_time = {}  # Track when we last sent a notification to the user
        self.limit = limit
        self.update_types = ['message']
        self.bot: AsyncTeleBot = _bot
        self.logger = logger

    async def pre_process(self, message: Message, data):
        if message.content_type == "photo":
            return ContinueHandling()

        user_id = message.from_user.id
        chat_id = message.chat.id
        message_id = message.message_id
        current_time = message.date

        last_message_time = self.last_time.get(user_id, 0)
        last_notification_time = self.notification_time.get(user_id, 0)
        time_diff = current_time - last_message_time
        notification_time_diff = current_time - last_notification_time

        if 0 < time_diff <= self.limit:
            self.logger.info(f"Deleting message from user {user_id} due to rate limit")
            await self.bot.delete_message(chat_id, message_id)

            if notification_time_diff >= self.limit:
                await self.bot.send_message(chat_id, "Iltimos, Ko'p habar jo'natmang")
                self.notification_time[user_id] = current_time

            return CancelUpdate()

        self.last_time[user_id] = current_time

    async def post_process(self, message, data, exception):
        pass


# bot.setup_middleware(SimpleMiddleware(1, bot))


async def bot_meta():
    await bot.delete_my_commands()
    await bot.set_my_commands(commands=[BotCommand("start", "Botni boshlash")])
