import hashlib
import uuid
from typing import Tuple, List, Any
from loader import dataBase
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from data.config import settings
from data.lexicon import lexicon
from datetime import datetime as dt
from loader import dataBase


class menu_cd(CallbackData, prefix="show_menu"):
    level: int = 0
    restaurant_worksheet_id: str = "0"
    status: str = "0"
    dish_name: str = "0"
    photo_path: str = "0"
    description: str = "0"
    surname_chef: str = "0"
    final_status: str = "0"
    ref_id: str = "0"
    start_menu: str = "0"
    section: str = "0"
    dish_id: str = "0"


class welcome_cd(CallbackData, prefix="welcome_menu"):
    level: int = 0
    start_menu: str = "0"
    phone_number: str = "0"
    surname: str = "0"
    role: str = "0"


async def restaurant_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    # current menu level 0
    CURRENT_LEVEL = 0

    # Creating a keyboard
    per_page = 6
    items = list(settings.worksheet_ids.items())
    start = page * per_page
    end = start + per_page
    sliced = items[start:end]

    markup = InlineKeyboardBuilder()

    # Кнопки ресторанов (по 2 в ряд)
    buttons = []
    for name, rest_id in sliced:
        buttons.append(InlineKeyboardButton(
            text=name,
            callback_data=menu_cd(
                level=CURRENT_LEVEL + 1, restaurant_worksheet_id=rest_id, start_menu="rest_menu"
            ).pack(),
        ))
    markup.row(*buttons, width=2)
    # Стрелки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page:{page - 1}"))
    if page == 0:
        nav_buttons.append(InlineKeyboardButton(text=" ", callback_data="0"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page:{page + 1}"))
    if end > len(items):
        nav_buttons.append(InlineKeyboardButton(text=" ", callback_data="0"))

    if nav_buttons:
        markup.row(*nav_buttons)

    return markup.as_markup()


def request_contact_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=lexicon["phone_number"], request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


async def roles_keyboard(phone_number: str = "0") -> InlineKeyboardMarkup:
    items = list(settings.roles.items())
    markup = InlineKeyboardBuilder()
    buttons = []
    for role, description in items:
        buttons.append(InlineKeyboardButton(
            text=description,
            callback_data=welcome_cd(
                start_menu="surname", phone_number=phone_number, role=role
            ).pack(),
        ))
    return markup.row(*buttons, width=2).as_markup()


async def solo_restaurant_keyboard(restaurant_id: str, count_check_reviews: int) -> InlineKeyboardMarkup:
    # current menu level 1
    CURRENT_LEVEL = 1
    markup = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=lexicon["new_review"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 2,
                                  restaurant_worksheet_id=restaurant_id,
                                  start_menu="new_review",
                                  ).pack(),
        ),
        InlineKeyboardButton(
            text=lexicon["check_latest"].format(count=count_check_reviews),
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=restaurant_id,
                                  start_menu="check_latest",
                                  ).pack(),
        ),
        InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(
                level=CURRENT_LEVEL - 1, start_menu="start_menu"
            ).pack(),
        ),
    ]
    return markup.row(*buttons, width=1).as_markup()


async def status_keyboard(message: Any, callback_data: menu_cd) -> InlineKeyboardMarkup:
    # current menu level 3
    CURRENT_LEVEL = 3
    restaurant_worksheet_id = callback_data.restaurant_worksheet_id
    markup = InlineKeyboardBuilder()
    buttons = []
    if callback_data.ref_id == "0":
        buttons.extend([InlineKeyboardButton(
            text=lexicon["status_error"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=restaurant_worksheet_id,
                                  start_menu="status_error",
                                  status="error",
                                  ).pack(),
                ),
            InlineKeyboardButton(
            text=lexicon["status_opinion"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=restaurant_worksheet_id,
                                  start_menu="status_opinion",
                                  status="opinion",
                                  ).pack(),
                ),
            InlineKeyboardButton(
            text=lexicon["status_check"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=restaurant_worksheet_id,
                                  start_menu="status_check",
                                  status="check",
                                  ).pack(),
                ),
            ]
        )
    else:
        buttons.append(InlineKeyboardButton(
            text=lexicon["status_check"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=restaurant_worksheet_id,
                                  start_menu="status_check",
                                  status="check",
                                  ref_id=callback_data.ref_id
                                  ).pack(),
            )
        )
    buttons.append(InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(level=CURRENT_LEVEL - 2,
                                  restaurant_worksheet_id=restaurant_worksheet_id,
                                  start_menu="rest_menu",
                                  ).pack(),
        )
    )
    return markup.row(*buttons, width=1).as_markup()


async def back_button(callback_data: menu_cd) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=lexicon["button_back"],
        callback_data=menu_cd(
            level=callback_data.level - 1,
            start_menu="new_review",
            status="0",
            restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
        ).pack(),
    )
    return builder.as_markup()


def back_from_state_to_status(callback_data: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=lexicon["button_back"],
                callback_data=menu_cd(
                    start_menu="new_review",
                    status="0",
                    restaurant_worksheet_id=callback_data["restaurant_worksheet_id"]
                ).pack()
            )
        ]
    ])


async def final_status_keyboard(message: Any, callback_data: menu_cd) -> InlineKeyboardMarkup:
    # current menu level 6
    CURRENT_LEVEL = 6
    markup = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=lexicon["status_final_remake"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
                                  status=callback_data.status,
                                  start_menu="final_status",
                                  final_status="remake"

                                  ).pack(),
        ),
        InlineKeyboardButton(
            text=lexicon["status_final_good"],
            callback_data=menu_cd(level=CURRENT_LEVEL + 1,
                                  restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
                                  status=callback_data.status,
                                  start_menu="final_status",
                                  final_status="good"

                                  ).pack(),
        ),
        InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(
                start_menu="new_review",
                status="0",
                restaurant_worksheet_id=callback_data.restaurant_worksheet_id
            ).pack()
        ),
    ]
    return markup.row(*buttons, width=1).as_markup()


async def accept_final_keyboard(message: Any, callback_data: menu_cd) -> InlineKeyboardMarkup:
    # current menu level 7
    CURRENT_LEVEL = 7
    markup = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(
                start_menu="new_review",
                status="0",
                restaurant_worksheet_id=callback_data.restaurant_worksheet_id
            ).pack()
        ),
        InlineKeyboardButton(
            text=lexicon["button_accept"],
            callback_data=menu_cd(
                level=0,
                restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
                status=callback_data.status,
                final_status=callback_data.final_status,
                start_menu="a_r_m"
            ).pack(),
        ),
    ]
    return markup.row(*buttons, width=2).as_markup()


async def check_latest_keyboard(message: Any, restaurant_worksheet_id, page: int = 0) -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 2
    per_page = 5
    reviews = dataBase.get_reviews_for_check(restaurant_worksheet_id)

    total_pages = (len(reviews) - 1) // per_page + 1  # считаем количество страниц

    start = page * per_page
    end = start + per_page
    sliced = reviews[start:end]

    markup = InlineKeyboardBuilder()
    buttons = []

    for review in sliced:
        review_date = dt.strptime(review['rev_date'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m")
        buttons.append(InlineKeyboardButton(
            text=f"{review_date} - {review['dish_name']}",
            callback_data=menu_cd(
                level=CURRENT_LEVEL + 1,
                restaurant_worksheet_id=review["worksheet_id"],
                start_menu="new_review",
                ref_id=str(review["id"])
            ).pack(),
        ))
    markup.row(*buttons, width=1)

    # пагинация (стрелки влево/вправо)
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"pagecheck:{page - 1}"
            )
        )
    if page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"pagecheck:{page + 1}"
            )
        )
    if pagination_buttons:
        markup.row(*pagination_buttons)

    # кнопка "Назад"
    back_button = InlineKeyboardButton(
        text=lexicon["button_back"],
        callback_data=menu_cd(
            level=CURRENT_LEVEL - 1,
            restaurant_worksheet_id=restaurant_worksheet_id,
            start_menu="rest_menu"
        ).pack(),
    )
    markup.row(back_button)

    return markup.as_markup()


async def category_dishes_keyboard(message: Any, callback_data: menu_cd):
    CURRENT_LEVEL = 4
    restaurant_worksheet_id = callback_data.restaurant_worksheet_id

    if not dataBase.table_exists(str(restaurant_worksheet_id)):
        return back_button(callback_data)

    sections = dataBase.get_sections(str(restaurant_worksheet_id))
    markup = InlineKeyboardBuilder()

    # Кнопки разделов
    for row in sections:
        section_name = row["section"]
        section_hash = hashlib.md5(section_name.encode("utf-8")).hexdigest()[:8]
        markup.row(
            InlineKeyboardButton(
                text=section_name,
                callback_data=menu_cd(
                    level=CURRENT_LEVEL + 1,
                    restaurant_worksheet_id=restaurant_worksheet_id,
                    section=section_hash,
                    start_menu="s_n_d"
                ).pack()
            ),
            width=1
        )

    markup.row(
        InlineKeyboardButton(
            text="Open food",
            callback_data=menu_cd(
                level=CURRENT_LEVEL + 1,
                restaurant_worksheet_id=restaurant_worksheet_id,
                section="open_food",
                start_menu="open_food",
                dish_id="none"
            ).pack()
        )
    )
    # Кнопка назад
    markup.row(
        InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(
                level=CURRENT_LEVEL - 1,
                restaurant_worksheet_id=restaurant_worksheet_id,
                start_menu="new_review",
            ).pack()
        )
    )

    return markup.as_markup()


async def dishes_by_category_keyboard(message: Any, callback_data: menu_cd, page: int = 0) -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 5
    restaurant_worksheet_id = callback_data.restaurant_worksheet_id
    section = dataBase.get_name_section_by_hash(restaurant_worksheet_id, callback_data.section)

    dishes = dataBase.get_dishes_by_section(str(restaurant_worksheet_id), section)

    markup = InlineKeyboardBuilder()
    buttons = []
    for dish in dishes:
        buttons.append(InlineKeyboardButton(
            text=dish["dish_name"],
            callback_data=menu_cd(
                level=CURRENT_LEVEL,
                restaurant_worksheet_id=restaurant_worksheet_id,
                start_menu="open_food",
                dish_id=str(dish["id"]),
            ).pack(),
        ))
    markup.row(*buttons, width=1)

    # open food button
    markup.row(
        InlineKeyboardButton(
            text="Open food",
            callback_data=menu_cd(
                level=CURRENT_LEVEL,
                restaurant_worksheet_id=restaurant_worksheet_id,
                section="open_food",
                start_menu="open_food",
                dish_id="none"
            ).pack()
        )
    )
    # Кнопка назад
    markup.row(
        InlineKeyboardButton(
            text=lexicon["button_back"],
            callback_data=menu_cd(
                level=CURRENT_LEVEL - 1,
                restaurant_worksheet_id=restaurant_worksheet_id,
                start_menu="new_review"
            ).pack()
        )
    )

    return markup.as_markup()
