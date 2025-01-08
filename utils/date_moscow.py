from datetime import datetime

import pytz
from aiogram.utils import markdown


def get_current_date(time_date: bool):
        moscow_tz = pytz.timezone('Europe/Moscow')
        return datetime.now(moscow_tz).date() if time_date is True\
            else datetime.now(moscow_tz).strftime(f"Дата: {markdown.hbold('%Y-%m-%d')},"
                                                  f" Время: {markdown.hbold('%H:%M')}"
                                                  )