import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage # Для FSM
from dotenv import load_dotenv

from bot.handlers import router as main_router # Убедитесь, что путь правильный

async def main():
    load_dotenv() # Загружаем переменные из .env в корне проекта
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logging.error("TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    bot = Bot(token=bot_token)
    # storage = RedisStorage.from_url(os.getenv("REDIS_URL")) # для production
    storage = MemoryStorage() # для разработки
    dp = Dispatcher(storage=storage)

    dp.include_router(main_router)
    
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot starting...")

    # Удаляем вебхук, если он был установлен ранее
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Убедитесь, что вы находитесь в корневой папке проекта при запуске
    # python -m bot.main_bot (если запускаете как модуль)
    # или настройте PYTHONPATH
    # Для простоты, если main_bot.py в bot/, а запускаем из корня:
    # PYTHONPATH=. python bot/main_bot.py
    # Или можно сделать запускающий скрипт в корне проекта:
    # run_bot.py
    # ```python
    # #!/usr/bin/env python
    # import asyncio
    # from bot.main_bot import main
    #
    # if __name__ == '__main__':
    #     asyncio.run(main())
    # ```
    # И затем: python run_bot.py
    asyncio.run(main())