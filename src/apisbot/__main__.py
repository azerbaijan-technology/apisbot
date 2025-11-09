import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from apisbot.bot.commands.start import set_start_commands

# Import handlers
from .bot.dialogs import get_birth_data_dialog
from .bot.handlers import chart_flow, composite_flow, start
from .bot.middlewares import LoggingMiddleware
from .config import get_settings

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the Telegram bot."""
    # Load configuration
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Telegram Natal Chart Bot")

    # Create bot instance
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await set_start_commands(bot)

    # Create FSM storage with session timeout
    storage = MemoryStorage()

    # Create dispatcher
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.update.middleware(LoggingMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(chart_flow.router)
    dp.include_router(composite_flow.router)

    # Register dialogs for calendar and time picker widgets (T037-T038)
    birth_data_dialog = get_birth_data_dialog()
    dp.include_router(birth_data_dialog)

    # Setup aiogram-dialog
    setup_dialogs(dp)

    logger.info(f"Bot configured with session timeout: {settings.session_timeout}s")
    logger.info("Dialogs registered: birth_data_dialog (calendar + time picker)")
    logger.info("Starting polling...")

    try:
        # Start bot
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
