__all__ = 'router'

from aiogram import Router

router = Router(name=__name__)
from callback_handlers.callback_handlers import router as handler_router
from callback_handlers.pay_func import router as pay_handlers

from callback_handlers.pay_handler import router as pay_callback_handler

router.include_routers(
    pay_handlers,
    pay_callback_handler,
    handler_router,
)
