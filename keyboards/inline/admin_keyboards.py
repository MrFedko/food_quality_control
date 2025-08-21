from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.lexicon import lexicon


async def start_super_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="button_mail", callback_data="mail"),
        InlineKeyboardButton(text="db_button", callback_data="db_api"),
        InlineKeyboardButton(text="fast_request", callback_data="fast_requests"),
    ]
    return markup.row(*buttons, width=2).as_markup()
