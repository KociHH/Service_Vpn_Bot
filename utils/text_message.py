from bd_api.middle import logger


async def send_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Сообщение отправлено пользователю {chat_id}.")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {chat_id}: {e}")