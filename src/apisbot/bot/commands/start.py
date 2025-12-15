from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_start_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Start the bot and initialize your session"),
        BotCommand(command="help", description="❓ Get help and view available commands"),
        BotCommand(command="cancel", description="❌ Cancel current operation and return to main menu"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
