__all__ = 'router'

from aiogram import Router
from commands.common import router as ammo_router
from callback_handlers import router as ammo_callback_router

router = Router(name=__name__)
router.include_routers(ammo_router, ammo_callback_router)
