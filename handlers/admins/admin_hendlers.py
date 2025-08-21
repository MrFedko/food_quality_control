from asyncio import sleep
from typing import Union
from aiogram import F as f
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram import types, Router
from loader import dataBase
from keyboards.inline.admin_keyboards import start_super_keyboard
from keyboards.inline.menu_keyboards import restaurant_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from states.admin import super_panel
from aiogram.filters.command import Command
from data.config import settings
from data.lexicon import lexicon
from loader import bot

router = Router()


@router.message(Command("menu"), flags={"chat_action": "typing"})
async def admin_panel(message: types.Message):
    await list_super_menu(message)


@router.message(Command("dbstart"), flags={"chat_action": "typing"})
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in settings.admins:
        dataBase.create_table_users()
        dataBase.create_table_reviews()
        await list_super_menu(message)


async def list_super_menu(message: Union[types.Message, types.CallbackQuery]):
    if str(message.from_user.id) in settings.admins:
    #     markup = await start_super_keyboard()
    #     if isinstance(message, types.Message):
    #         await message.answer(lexicon['/menu'], reply_markup=markup)
    #     elif isinstance(message, types.CallbackQuery):
    #         call = message
    #         await call.message.edit_text(lexicon["/menu"], reply_markup=markup)
    #         await call.answer()
    # else:
    #     if isinstance(message, types.CallbackQuery):
    #         call = message
    #         markup = await start_keyboard()
    #         await call.message.edit_text(lexicon["echo"], reply_markup=markup)
    #         await call.answer()
    #     elif isinstance(message, types.Message):
    #         markup = await start_keyboard()
    #         await message.answer(lexicon["echo"], reply_markup=markup)
        pass
