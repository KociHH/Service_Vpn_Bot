from aiogram.fsm.state import StatesGroup, State

class Admin(StatesGroup):
    admin = State()

    file = State()
    check_file = State()

    user_history_payments = State()

class NewSletterState(StatesGroup):
    rassilka = State()
    check_rassilka = State()
    change_content = State()
    change_text_caption = State()
    waiting_for_media_group_end = State()


class PaymentsUserState(StatesGroup):
    payments_menu = State()