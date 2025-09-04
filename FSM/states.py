from aiogram.fsm.state import StatesGroup, State

class Admin(StatesGroup):
    admin = State()
    rassilka = State()
    chek_rassilka = State()

    file = State()
    check_file = State()

    user_history_payments = State()
