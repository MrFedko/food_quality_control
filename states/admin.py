from aiogram.filters.state import State, StatesGroup


class super_panel(StatesGroup):
    mail = State()
    settings = State()
    db_settings = State()
    server_crud = State()
    user_crud = State()
    order_crud = State()
    prod_crud = State()
    new_cost = State()
    new_server = State()
    keys_crud = State()
    fast_req = State()
    download_config = State()
    send_message = State()
    server_count = State()
    key_admin = State()
