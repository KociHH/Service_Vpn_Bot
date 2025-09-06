__all__ = 'router'

from aiogram import Router

router = Router(name=__name__)
from callback_handlers.common import router as common_router
from callback_handlers.pay_func import router as pay_handlers

from callback_handlers.payment_part import router as payment_part_handler

router.include_routers(
    pay_handlers,
    payment_part_handler,
    common_router,
)
