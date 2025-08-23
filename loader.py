from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from data.config import settings
from database.crud import Database
from fastapi import FastAPI

from utils.dropbox import DropboxClient
from utils.sheet_utils.sheet_control import GoogleSheetsClient

session = AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dataBase = Database(settings.DB_PATH)
appFA = FastAPI()
client = GoogleSheetsClient(
    creds_path="quality-control-469712-5f601fa34788.json",
    sheet_id=settings.SHEET_ID
)
clientDB = DropboxClient(settings.DB_KEY, settings.DB_SECRET, settings.DROPBOX_TOKEN)
