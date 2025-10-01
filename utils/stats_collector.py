import asyncio
import os
from datetime import datetime, timedelta
from collections import Counter
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError


class WeeklyStats:
    def __init__(self, database, bot, worksheet_ids):
        self.db = database
        self.bot = bot
        self.worksheet_ids = worksheet_ids

    async def run_loop(self):
        while True:
            now = datetime.now()
            # ближайший понедельник 12:00
            days_ahead = (7 - now.weekday()) % 7
            next_run = now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
            if next_run <= now:
                next_run += timedelta(days=7)

            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self.send_stats()

    def prepare_stats(self):
        now = datetime.now()
        start_cur = now - timedelta(days=7)
        start_prev = now - timedelta(days=14)
        end_prev = start_cur

        current = self.db.get_reviews(start_cur, now)
        previous = self.db.get_reviews(start_prev, end_prev)

        stats = {}
        for ws_name, ws_id in self.worksheet_ids.items():
            cur_data = [r for r in current if r["worksheet_id"] == ws_id]
            prev_data = [r for r in previous if r["worksheet_id"] == ws_id]

            if not cur_data:
                continue

            # ошибки
            errors = [r for r in cur_data if r["status"].lower() == "ошибка"]
            errors_prev = [r for r in prev_data if r["status"].lower() == "ошибка"]

            # проверки
            checks = [r for r in cur_data if r["status"].lower() in ("контроль качества",)]

            # динамика
            prev_count = len(errors_prev)
            curr_count = len(errors)
            if prev_count > 0:
                dynamic = (curr_count - prev_count) / prev_count * 100
            else:
                dynamic = float("inf") if curr_count > 0 else 0

            # лидеры по блюдам с количеством ошибок
            dish_counter = Counter([r["dish_name"].strip().lower() for r in errors])
            dish_leaders = [
                f"{name} <b>({count} ошибки)</b>" if count > 1 else name
                for name, count in dish_counter.most_common(2)
            ]

            # лидер по су-шефам
            chef_counter = Counter([r["surname_chef"].strip().lower() for r in errors])
            raw_name = chef_counter.most_common(1)[0][0] if chef_counter else None
            chef_leader = raw_name.capitalize() if raw_name else None

            stats[ws_name] = {
                "errors": curr_count,
                "checks": len(checks),
                "dynamic": dynamic,
                "dish_leaders": dish_leaders,
                "chef_leader": chef_leader
            }
        return stats

    async def send_stats(self):
        users = ("224056242", "356317940", "856450052", os.getenv("ADMIN_ID"))
        users = [{"user_tg_id": int(u)} for u in users if u]
        stats = self.prepare_stats()

        if not stats:
            return

        now = datetime.now()
        start_period = (now - timedelta(days=7)).strftime("%d.%m")
        end_period = now.strftime("%d.%m")

        header = f"📊 Еженедельная статистика контроля качества ({start_period} — {end_period})"

        messages = [header]  # массив сообщений
        no_control = []

        for rest_name, rest_id in self.worksheet_ids.items():
            if rest_name not in stats:
                no_control.append(rest_name)
                continue

            s = stats[rest_name]
            dynamic_str = (
                f"{s['dynamic']:+.1f}%" if isinstance(s['dynamic'], (int, float)) and s['dynamic'] != float('inf')
                else "0%"
            )
            block = (
                f"🏛 {rest_name}\n"
                f"<b>Ошибок:</b> {s['errors']}\n"
                f"<b>Контролей:</b> {s['checks']}\n"
                f"<b>Динамика к прошлой неделе:</b> {dynamic_str}\n"
                f"<b>Топ блюда по ошибкам:</b> {', '.join(s['dish_leaders']) if s['dish_leaders'] else '—'}\n"
                f"<b>Лидер по ошибкам (су-шеф):</b> {s['chef_leader'] or '—'}"
            )

            # проверяем длину блока
            if len(block) > 4000:
                # на случай очень длинного текста – режем внутри
                for i in range(0, len(block), 4000):
                    messages.append(block[i:i + 4000])
            else:
                messages.append(block)

        if no_control:
            messages.append("🚫<b> Без контроля:</b> " + ", ".join(no_control))

        # рассылаем
        for u in users:
            for msg in messages:
                try:
                    await self.bot.send_message(u["user_tg_id"], msg)
                except Exception as e:
                    await self.bot.send_message(
                        os.getenv("ADMIN_ID"),
                        f"Ошибка отправки {u['user_tg_id']}: {e}"
                    )
