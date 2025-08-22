from aiogram.filters.state import State, StatesGroup


class user_panel(StatesGroup):
    surname = State()
    new_review = State()
