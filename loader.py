from utils.states import *
from utils.config import TOKEN
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from utils import bot_logger, log_level

bot_logger.init_custom_logger(log_level)

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.ChatFilter())

auth_sts = Auth()
user_sts = UserState()
stadium_sts = StadiumState()
manage_sts = ManageStadiums()
help_sts = Help()
admin_sts = SuperUserState()
owner_sts = OwnerState()
neutral_sts = NeutralState()
admin_menu_sts = AdminMenu()