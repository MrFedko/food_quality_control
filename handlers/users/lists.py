from aiogram.types import CallbackQuery, Message
from typing import Union
import datetime
from data.lexicon import lexicon
from loader import dataBase
from keyboards.inline.menu_keyboards import \
    (restaurant_keyboard,
     request_contact_keyboard,
     roles_keyboard,
     solo_restaurant_keyboard,
     status_keyboard, menu_cd
     )


async def list_restaurant_menu(message: Union[CallbackQuery, Message], **kwargs):
    markup = await restaurant_keyboard()
    text = lexicon["/start"].format(name=message.from_user.first_name)

    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_welcome_menu(message: Union[CallbackQuery, Message], **kwargs):
    markup = request_contact_keyboard()
    text = lexicon["welcome"].format(name=message.from_user.first_name)

    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_role_menu(message: Union[CallbackQuery, Message], **kwargs):
    markup = await roles_keyboard(message.contact.phone_number)
    text = lexicon["choose_role"]
    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_solo_restaurant_menu(message: Union[CallbackQuery, Message], **kwargs):
    restaurant_id = str(kwargs.get("restaurant_id"))
    markup = await solo_restaurant_keyboard(restaurant_id)
    text = lexicon["solo_restaurant_menu"]
    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_status_review(message: Union[CallbackQuery, Message], callback_data: menu_cd, **kwargs):
    markup = await status_keyboard(message, callback_data)
    text = lexicon["status_review"]
    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)
