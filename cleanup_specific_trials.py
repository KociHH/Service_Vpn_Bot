"""
Скрипт для очистки пробных подписок конкретных пользователей (старая схема)
"""
import asyncio
import logging
from db.tables import TrialSubscription, async_session
from kos_Htools.sql.sql_alchemy.dao import BaseDAO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Список пользователей для очистки (используют старую схему)
USER_IDS = [1896661232, 1958773156, 7579305402]


async def cleanup_specific_trials():
    """Очищает пробные подписки конкретных пользователей (старая схема без vless_link_id)"""
    logger.info(f"Начинаем очистку пробных подписок для {len(USER_IDS)} пользователей (старая схема)...")
    
    async with async_session() as db_session:
        trial_dao = BaseDAO(TrialSubscription, db_session)
        
        cleaned_count = 0
        for user_id in USER_IDS:
            # Получаем триальную подписку пользователя
            trial = await trial_dao.get_one(TrialSubscription.user_id == user_id)
            
            if not trial:
                logger.warning(f"Пробная подписка для пользователя {user_id} не найдена")
                continue
            
            # Обнуляем триальную подписку (без удаления ключа, т.к. его нет в новой схеме)
            await trial_dao.update(
                TrialSubscription.user_id == user_id,
                {
                    "start_date": None,
                    "end_date": None,
                    "trial_used": True,
                    "vless_link_id": None
                }
            )
            logger.info(f"✅ Очищена пробная подписка пользователя {user_id} (старая схема)")
            cleaned_count += 1
        
        logger.info(f"✅ Всего очищено {cleaned_count} пробных подписок")


if __name__ == "__main__":
    asyncio.run(cleanup_specific_trials())
