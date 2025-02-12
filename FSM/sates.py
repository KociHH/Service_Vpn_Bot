from aiogram.fsm.state import StatesGroup, State

# States Email
class Email(StatesGroup):
    email = State()
    action = State()
    data = State()

# States Admin
class Admin(StatesGroup):
    admin = State()
    rassilka = State()
    chek_rassilka = State()

    file = State()
    check_file = State()

