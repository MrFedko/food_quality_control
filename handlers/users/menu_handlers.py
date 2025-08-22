import asyncio
import os
import json
import datetime
import time
from aiogram.enums import ContentType
from aiogram import types, F as f, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from magic_filter import F as MF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loader import dataBase, dp, bot
from data.config import settings
from data.lexicon import lexicon
from keyboards.inline.menu_keyboards import menu_cd, welcome_cd, restaurant_keyboard
from states.user import user_panel
from .lists import (
    list_restaurant_menu,
    list_welcome_menu,
    list_role_menu,
    list_solo_restaurant_menu,
    list_status_review
)

router = Router()


@router.message(Command("start"), flags={"chat_action": "typing"})
async def show_menu(message: types.Message):
    if not dataBase.read_user(message.from_user.id):
        await list_welcome_menu(message)
    else:
        await list_restaurant_menu(message)


@router.callback_query(
    menu_cd.filter(MF.start_menu == "start_menu"), flags={"chat_action": "typing"}
)
async def restaurant_menu_handler(callback: CallbackQuery, callback_data: menu_cd):
    await list_restaurant_menu(callback)


@dp.callback_query(lambda c: c.data.startswith("page:"))
async def page_handler(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(reply_markup=await restaurant_keyboard(page=page))
    await callback.answer()


@router.message(f.content_type == ContentType.CONTACT)
async def choose_city(message: types.Message):
    confirm_msg = await message.answer(
        "Спасибо, номер получен ✅",
        reply_markup=ReplyKeyboardRemove()
    )
    await asyncio.sleep(1)
    await confirm_msg.delete()
    await list_role_menu(message)


@router.callback_query(
    welcome_cd.filter(MF.start_menu == "surname"), flags={"chat_action": "typing"}
)
async def welcome_surname(call: CallbackQuery, callback_data: welcome_cd, state: FSMContext):
    await state.update_data(role=callback_data.role, phone_number=callback_data.phone_number)
    await call.message.edit_text(lexicon["welcome_surname"])
    await call.answer()
    await state.set_state(user_panel.surname)


@router.message(StateFilter(user_panel.surname), flags={"chat_action": "typing"})
async def welcome_surname_handler(message: types.Message, state: FSMContext):
    surname = message.text.strip()
    data = await state.get_data()
    role = data.get("role")
    phone_number = data.get("phone_number")
    dataBase.new_user(message.from_user.username, surname, message.from_user.id, role, phone_number)
    await list_restaurant_menu(message)
    await state.clear()


@router.callback_query(
    menu_cd.filter(MF.start_menu == "rest_menu"), flags={"chat_action": "typing"}
)
async def restaurant_menu_handler(callback: CallbackQuery, callback_data: menu_cd):
    await callback.message.delete_reply_markup()
    await list_solo_restaurant_menu(callback)


@router.callback_query(
    menu_cd.filter(MF.start_menu == "new_review"), flags={"chat_action": "typing"}
    )
async def new_review_handler(callback: CallbackQuery, callback_data: menu_cd, state: FSMContext):
    await callback.message.edit_text(lexicon["new_review"])
    await callback.answer()
    await list_status_review(callback, callback_data)
