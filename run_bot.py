#!/usr/bin/env python
import asyncio
import sys
import os

# Добавляем корень проекта в PYTHONPATH, чтобы работали относительные импорты
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bot.main_bot import main

if __name__ == '__main__':
    asyncio.run(main())