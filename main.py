import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers.menu_handlers import router as menu_router
from handlers.order_handlers import router as order_router
from handlers.common import router as common_router

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register all routers
    dp.include_router(common_router)
    dp.include_router(menu_router)
    dp.include_router(order_router)
    
    # Set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])
    
    # Start polling
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main()) 