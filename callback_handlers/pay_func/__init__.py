__all__ = 'router'

from aiogram import Router
from .pay_yookassa import router as pay_router
router = Router()

router.include_routers(pay_router)


