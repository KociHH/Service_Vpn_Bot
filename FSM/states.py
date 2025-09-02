from aiogram.fsm.state import StatesGroup, State

class Email(StatesGroup):
    email = State()
    action = State()
    data = State()

class Admin(StatesGroup):
    admin = State()
    rassilka = State()
    chek_rassilka = State()

    file = State()
    check_file = State()

