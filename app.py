# app.py
import asyncio
from aiogram.utils.chat_action import ChatActionMiddleware
from data.config import settings
from handlers.users import menu_handlers
from handlers.admins import admin_hendlers, help
from loader import dp, watcher, weekly_stats, create_bot
from utils.misc.set_bot_commands import set_default_commands
from utils.misc.notify_admins import on_startup_notify, on_shutdown_notify

async def on_startup(bot):
    await set_default_commands(bot)
    await on_startup_notify(bot)

async def on_shutdown(bot):
    await on_shutdown_notify(bot)

def connect_routers():
    dp.include_routers(help.router, menu_handlers.router, admin_hendlers.router)

async def main():
    # создаём бота через SOCKS5/VLESS
    bot = await create_bot()

    # подключаем middleware и роутеры до polling
    dp.message.middleware.register(ChatActionMiddleware())
    connect_routers()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # удаляем webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем фоновые задачи
    asyncio.create_task(watcher.run_loop(bot))
    asyncio.create_task(weekly_stats.run_loop(bot))

    # polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
