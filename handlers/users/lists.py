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
     status_keyboard,
     menu_cd,
     final_status_keyboard,
     accept_final_keyboard,
     check_latest_keyboard
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


async def list_solo_restaurant_menu(message: Union[CallbackQuery, Message], callback_data: menu_cd):
    restaurant_id = callback_data.restaurant_worksheet_id
    count_check_reviews = dataBase.count_check_reviews(restaurant_id)
    markup = await solo_restaurant_keyboard(restaurant_id, count_check_reviews)
    text = lexicon["solo_restaurant_menu"]
    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_status_review(message: Union[CallbackQuery, Message], callback_data: menu_cd, **kwargs):
    markup = await status_keyboard(message, callback_data)
    if callback_data.ref_id == "0":
        text = lexicon["status_review"]
    else:
        dish_name, description = dataBase.get_dish_info(callback_data.ref_id)
        text = lexicon["check_latest_dish"].format(description=description, dish_name=dish_name)
    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=markup)


async def list_final_status(message: Union[CallbackQuery, Message], callback_data: dict, **kwargs):
    restaurant_worksheet_id = callback_data["restaurant_worksheet_id"]
    status = callback_data["status"]
    photo_path = callback_data["photo_path"]
    menucd = menu_cd(
        level=6,
        restaurant_worksheet_id=restaurant_worksheet_id,
        status=status,
        photo_path=photo_path,
    )
    markup = await final_status_keyboard(message, menucd)
    await message.answer(lexicon["final_status"], reply_markup=markup)


async def list_accept_final(callback: CallbackQuery, callback_data: menu_cd, **kwargs):
    markup = await accept_final_keyboard(callback, callback_data)
    await callback.message.edit_reply_markup(reply_markup=markup)


async def list_check_latest(callback: CallbackQuery, restaurant_worksheet_id, **kwargs):
    markup = await check_latest_keyboard(callback, restaurant_worksheet_id)
    await callback.message.edit_reply_markup(reply_markup=markup)
