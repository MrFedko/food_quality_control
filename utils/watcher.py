import asyncio
import os
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError
import pytz


class Watcher:
    def __init__(self, database, bot):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
        self.database = database
        self.bot = bot
        self.messages = {
    0: "🕛 Полдень настал! Вспомните о контроле качества, а те, кто не на смене – наслаждайтесь белыми ночами или хотя бы белым хлебом 😉.",
    1: "Напоминание из Петербурга: проверьте продукты, внесите контроль, а если вы не на смене – прогуляйтесь вдоль Невы и отдохните 🌊.",
    2: "Менеджеры, пора взглянуть на блюда – вдруг они тоскуют без вашей проверки? А кто отдыхает – пусть отдыхает со вкусом ☕.",
    3: "Время проверять качество продуктов! А для тех, кто сегодня свободен – желаем культурного отдыха, как в Эрмитаже 🎨.",
    4: "Напоминаем о контроле качества! Кто не на смене – пусть наслаждается атмосферой Петербурга и звуками дождя 🌧️.",
    5: "Проверьте продукты, внесите результаты. А если выходной – пожелайте себе приятного чаепития под чтение Достоевского 📖.",
    6: "Контроль качества не ждёт! А свободным от смены мы рекомендуем прогулку по мостам (разведённым или нет – решать вам) 🌉.",
    7: "Менеджеры, продукты ждут внимания. Кто отдыхает – пусть наберётся сил и вдохновения, ведь это тоже часть качества ✨.",
    8: "Напоминание: контроль качества не спит. А для отдыхающих – желаем ленивого утра и интеллигентного безделья ☕🛋️.",
    9: "Петербургский полдень настал. Проверьте продукты! А тем, кто вне смены, – культурного отдыха и, возможно, встречи с Музой 🎶."
}

    def run(self):
        self.scheduler.add_job(self.check_end_date, trigger="cron", hour=16, minute=40)
        self.scheduler.start()

    async def check_end_date(self):
        data = self.database.get_managers()
        if not data:
            await self.bot.send_message(os.getenv("ADMIN_ID"), "Watcher: no managers found")
            return

        for user in data:
            message = random.choice(list(self.messages.values()))
            success = False
            while not success:
                try:
                    await self.bot.send_message(user["user_tg_id"], message)
                    success = True
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                except TelegramAPIError as e:
                    await self.bot.send_message(
                        os.getenv("ADMIN_ID"),
                        f"[!] User {user['user_tg_id']} not notified: {e}"
                    )
                    success = True
                except Exception as e:
                    await self.bot.send_message(
                        os.getenv("ADMIN_ID"),
                        f"[!] Unexpected error for user {user['user_tg_id']}: {e}"
                    )
                    success = True
            await asyncio.sleep(0.3)

        await self.bot.send_message(os.getenv("ADMIN_ID"), "Watcher: all messages sent successfully")

    def stop(self):
        self.scheduler.shutdown()
