from aiogram.utils.chat_action import ChatActionMiddleware
from multiprocessing import Process
from data.config import settings
from handlers.users import menu_handlers
from handlers.admins import admin_hendlers, help
import asyncio
from loader import dp, bot, dataBase, appFA
from utils.misc.set_bot_commands import set_default_commands
from utils.misc.notify_admins import on_startup_notify, on_shutdown_notify
import uvicorn


async def on_startup(bot):
    await set_default_commands(bot)
    await on_startup_notify(bot)


async def on_shutdown(bot):
    await on_shutdown_notify(bot)


def connect_routers():
    dp.include_routers(
        help.router, menu_handlers.router, admin_hendlers.router
    )


async def main():
    dp.message.middleware.register(ChatActionMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    connect_routers()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def run_fastapi():
    uvicorn.run("loader:appFA", host=settings.SERVER_IP, port=settings.SERVER_PORT)


def run_aiogram():
    from app import main
    asyncio.run(main())


if __name__ == "__main__":
    p1 = Process(target=run_fastapi)
    p1.start()

    p2 = Process(target=run_aiogram)
    p2.start()

    p1.join()
    p2.join()
