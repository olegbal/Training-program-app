import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import get_settings
from app.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def idle_without_token() -> None:
    logger.info("TELEGRAM_BOT_TOKEN is a placeholder; bot polling is disabled for local skeleton startup.")
    while True:
        await asyncio.sleep(3600)


async def main() -> None:
    settings = get_settings()
    if not settings.has_real_token:
        await idle_without_token()
        return

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher(settings=settings)
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
