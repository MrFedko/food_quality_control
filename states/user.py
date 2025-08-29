from aiogram.filters.state import State, StatesGroup


class user_panel(StatesGroup):
    surname = State()
    new_review = State()
    dish_name = State()
    description = State()
    price = State()
    photo = State()
    chef_surname = State()
    free = State()
