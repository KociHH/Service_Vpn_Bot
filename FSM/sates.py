from aiogram.fsm.state import StatesGroup, State

# States
class Email(StatesGroup):
    email = State()
    action = State()
    data = State()


class Admin(StatesGroup):
    admin = State()
    rassilka = State()
    chek_rassilka = State()
    edit_text = State()
