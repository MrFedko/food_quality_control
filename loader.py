from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from data.config import settings
from database.crud import Database
from utils.dropbox import DropboxClient
from utils.sheet_utils.sheet_control import GoogleSheetsClient
from utils.watcher import Watcher
from utils.stats_collector import WeeklyStats
from aiohttp_socks import ProxyConnector
import aiohttp

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация бота — внутри async
async def create_bot():
    connector = ProxyConnector.from_url("socks5://127.0.0.1:1080")
    session = AiohttpSession(connector=connector)
    bot = Bot(
        token=settings.BOT_TOKEN,
        parse_mode=ParseMode.HTML,
        session=session
    )
    return bot

session = AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dataBase = Database(settings.DB_PATH)
client = GoogleSheetsClient(
    creds_path="quality-control-469712-5f601fa34788.json",
    sheet_id=settings.SHEET_ID
)
clientDB = DropboxClient(settings.DB_KEY, settings.DB_SECRET, settings.DROPBOX_TOKEN)
watcher = Watcher(dataBase, bot)
weekly_stats = WeeklyStats(dataBase, bot, settings.worksheet_ids)
