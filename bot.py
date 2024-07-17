from database import populate_enums
from utils import bot_meta, log_level
from database.db_utils import create_models
from handlers.superusers import *
from handlers.owners import *
from handlers.users import *


async def main(instance):
    populate_enums()
    logger.info("bot_started")
    await create_models()
    await bot_meta()
    await instance.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    from loader import bot
    import asyncio
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    asyncio.run(main(bot))
