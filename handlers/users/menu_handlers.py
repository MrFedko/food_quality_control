import asyncio
import os
import uuid
import datetime
from aiogram.enums import ContentType
from aiogram import types, F as f, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from magic_filter import F as MF
from loader import dataBase, dp, client, clientDB
from data.config import settings
from data.lexicon import lexicon
from keyboards.inline.menu_keyboards import (menu_cd, welcome_cd, restaurant_keyboard,
                                             back_button, back_from_state_to_status,
                                             check_latest_keyboard,
                                             dishes_by_category_keyboard)
from states.user import user_panel
from .lists import (
    list_restaurant_menu,
    list_welcome_menu,
    list_role_menu,
    list_solo_restaurant_menu,
    list_status_review,
    list_final_status,
    list_accept_final,
    list_check_latest,
    list_category_dishes,
    list_dishes_by_category
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


@dp.callback_query(lambda c: c.data.startswith("pagecheck:"))
async def page_check_handler(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split(":")[1])
    data = await state.get_data()
    restaurant_worksheet_id = data.get("restaurant_worksheet_id")
    await callback.message.edit_reply_markup(
        reply_markup=await check_latest_keyboard(callback, restaurant_worksheet_id, page=page)
    )

    await callback.answer()


@router.message(f.content_type == ContentType.CONTACT)
async def choose_phone(message: types.Message):
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
    dataBase.new_user(message.from_user.username if message.from_user.username else message.from_user.first_name,
                      surname, message.from_user.id, role, phone_number)
    await list_restaurant_menu(message)
    await state.clear()


@router.callback_query(
    menu_cd.filter(MF.start_menu == "rest_menu"), flags={"chat_action": "typing"}
)
async def restaurant_menu_handler(callback: CallbackQuery, callback_data: menu_cd):
    await callback.message.delete_reply_markup()
    await list_solo_restaurant_menu(callback, callback_data)


@router.callback_query(
    menu_cd.filter(MF.start_menu == "new_review"), flags={"chat_action": "typing"}
    )
async def new_review_handler(callback: CallbackQuery, callback_data: menu_cd, state: FSMContext):
    await callback.message.edit_text(lexicon["new_review"])
    await list_status_review(callback, callback_data)
    await callback.answer()


@router.message(StateFilter(user_panel.dish_name), flags={"chat_action": "typing"})
async def dish_name_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        lexicon["dish_description"],
        reply_markup=back_from_state_to_status(data)
    )
    dish_name = message.text.strip()
    await state.update_data(dish_name=dish_name)
    await state.set_state(user_panel.description)


@router.message(StateFilter(user_panel.description), flags={"chat_action": "typing"})
async def description_handler(message: types.Message, state: FSMContext):
    dish_description = message.text.strip()
    await state.update_data(description=dish_description)
    data = await state.get_data()
    await message.answer(
        lexicon["dish_price"],
        reply_markup=back_from_state_to_status(data)
    )
    await state.set_state(user_panel.price)


@router.message(StateFilter(user_panel.price), flags={"chat_action": "typing"})
async def price_handler(message: types.Message, state: FSMContext):
    dish_price = message.text.strip()
    await state.update_data(price=dish_price)
    data = await state.get_data()
    await message.answer(
        lexicon["dish_image"],
        reply_markup=back_from_state_to_status(data)
    )
    await state.set_state(user_panel.photo)


@router.message(StateFilter(user_panel.photo), flags={"chat_action": "typing"})
async def photo_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    restaurant_id = data.get("restaurant_worksheet_id")
    photo = message.photo[-1]
    unique_id = uuid.uuid4().hex[:4]
    filename = f"{restaurant_id}_{unique_id}.jpg"
    filepath = os.path.join(settings.PHOTO_DIR, filename)
    await message.bot.download(photo.file_id, destination=filepath)
    await message.answer(
        lexicon["chef_surname"],
        reply_markup=back_from_state_to_status(data)
    )
    await state.update_data(photo_path=filename)
    await state.set_state(user_panel.chef_surname)


@router.message(StateFilter(user_panel.chef_surname), flags={"chat_action": "typing"})
async def chef_surname_handler(message: types.Message, state: FSMContext):
    chef_surname = message.text.strip()
    await state.update_data(chef_surname=chef_surname)
    data = await state.get_data()
    await list_final_status(message, data)
    await state.set_state(user_panel.free)

@router.callback_query(
    menu_cd.filter(MF.start_menu == "final_status"), flags={"chat_action": "typing"}
)
async def final_status_handler(callback: types.CallbackQuery, callback_data: menu_cd, state: FSMContext):
    await state.update_data(final_status=callback_data.final_status)
    data = await state.get_data()
    restaurant_name = next((k for k, v in settings.worksheet_ids.items() if v == data["restaurant_worksheet_id"]), None)
    status = "Ошибка" if data["status"] == "error" else "Контроль качества"
    dish_name = data["dish_name"]
    description = data["description"]
    price = data["price"]
    surname_chef = data["chef_surname"]
    final_status = "Хорошо" if data["final_status"] == "good" else "На доработку"
    surname_reviewer = dataBase.read_user(callback.from_user.id)["surname"]
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    await state.update_data(surname_reviewer=dataBase.read_user(callback.from_user.id)["surname"])
    await callback.message.edit_text(lexicon["read_or_not"].format(restaurant_name=restaurant_name, status=status,
                                                                   dish_name=dish_name, description=description,
                                                                   price=price,
                                                                   surname_chef=surname_chef, final_status=final_status,
                                                                   surname_reviewer=surname_reviewer, date=date))
    await list_accept_final(callback, callback_data)
    await callback.answer()


@router.callback_query(
    menu_cd.filter(MF.start_menu == "a_r_m"), flags={"chat_action": "typing"}
)
async def again_restaurant_menu_handler(callback: CallbackQuery, callback_data: menu_cd, state: FSMContext):
    page = 0
    data = await state.get_data()
    worksheet_id = data["restaurant_worksheet_id"]
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    status = "Ошибка" if data["status"] == "error" else "Контроль качества"
    dish_name = data["dish_name"]
    photo_path = data["photo_path"]
    photo_pah_for_sheet = f"{settings.PHOTO_PATH}{photo_path}"
    remote_file = f"/photo/{os.path.basename(photo_pah_for_sheet)}"
    public_url = clientDB.upload_and_get_url(photo_pah_for_sheet, remote_file)
    public_url = public_url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
    description = data["description"]
    price = data["price"]
    surname_reviewer = dataBase.read_user(callback.from_user.id)["surname"]
    surname_chef = data["chef_surname"]
    final_status = "Хорошо" if callback_data.final_status == "good" else "На доработку"
    ref_id = data["ref_id"] if "ref_id" in data else "0"
    new_ref_id = uuid.uuid4().hex[:5]
    formula = "=IMAGE(\"" + public_url + "\"; 1)"
    formula_link = f'=HYPERLINK("{public_url}"; "Ссылка на фото")'
    await callback.message.edit_text(lexicon["review_sent"])
    if ref_id != "0":
        dataBase.update_ref_id(ref_id, new_ref_id if ref_id != "0" else ref_id)
    dataBase.new_review(worksheet_id, status, dish_name, photo_path, description, price, surname_reviewer, surname_chef, final_status, new_ref_id if ref_id != "0" else ref_id)
    await callback.message.edit_reply_markup(reply_markup=await restaurant_keyboard(page=page))
    await callback.answer()
    await client.insert_review_row(worksheet_id, date, status,
                                   dish_name, formula, description, price, surname_reviewer,
                                   surname_chef, final_status, formula_link, new_ref_id if ref_id != "0" else ref_id)
    await state.clear()


@router.callback_query(
    menu_cd.filter(MF.status != "0"), flags={"chat_action": "typing"}
    )
async def status_handler(callback: types.CallbackQuery, callback_data: menu_cd, state: FSMContext):
    if callback_data.ref_id == "0":
        await list_category_dishes(callback, callback_data)
        await callback.answer()
        await state.update_data(status=callback_data.status,
                                restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
                                )
        if dataBase.table_exists(callback_data.restaurant_worksheet_id):
            await state.set_state(user_panel.dish_category)
        else:
            await state.set_state(user_panel.dish_name)
    else:
        await callback.message.edit_text(lexicon["dish_description"], reply_markup=await back_button(callback_data))
        await callback.answer()
        await state.update_data(status=callback_data.status,
                                restaurant_worksheet_id=callback_data.restaurant_worksheet_id,
                                ref_id=callback_data.ref_id,
                                dish_name=dataBase.get_dish_info(callback_data.ref_id)[0]
                                )
        await state.set_state(user_panel.description)


# ветка проверки "На доработку"
@router.callback_query(
    menu_cd.filter(MF.start_menu == "check_latest"), flags={"chat_action": "typing"}
)
async def check_latest_handler(callback: CallbackQuery, callback_data: menu_cd, state: FSMContext):
    await callback.message.edit_text(lexicon["check_latest_menu"])
    await state.update_data(restaurant_worksheet_id=callback_data.restaurant_worksheet_id)
    await list_check_latest(callback, callback_data.restaurant_worksheet_id)
    await callback.answer()


@router.callback_query(
    menu_cd.filter(MF.start_menu == "open_food"), flags={"chat_action": "typing"}
)
async def open_food_handler(callback: types.CallbackQuery, callback_data: menu_cd, state: FSMContext):
    if callback_data.dish_id == "none":
        await state.set_state(user_panel.dish_name)
        await callback.message.edit_text(lexicon["dish_name"], reply_markup=await back_button(callback_data))
    else:
        dish = dataBase.get_dishes_by_id(callback_data.restaurant_worksheet_id, callback_data.dish_id)
        dish_name = f"{dish['section']} - {dish['dish_name']}"
        await state.update_data(dish_name=dish_name)
        await state.set_state(user_panel.description)
        await callback.message.edit_text(lexicon["dish_description"], reply_markup=await back_button(callback_data))
    await callback.answer()

@router.callback_query(
    menu_cd.filter(MF.start_menu == "s_n_d"), flags={"chat_action": "typing"}
)
async def page_dishes_handler(callback: types.CallbackQuery, callback_data: menu_cd, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.update_data(section=callback_data.section)
    await list_dishes_by_category(callback, callback_data)
