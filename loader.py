from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from data.config import settings
from database.crud import Database
from fastapi import FastAPI



session = AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dataBase = Database(settings.DB_PATH)
appFA = FastAPI()
