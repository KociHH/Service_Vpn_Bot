import logging

logger = logging.getLogger(__name__)


async def send_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Сообщение отправлено пользователю {chat_id}.")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {chat_id}: {e}")


async def samples_(texts: list):
    if not isinstance(texts, list):
        raise ValueError("Ожидается list[]")
    t = '—'
    result = []
    for text in texts:
        text = str(text).strip()
        line = t * (len(text) // 2)
        result.append(f'{text}\n{line}')
    print("t:",texts, "result:", result)
    return "\n\n".join(result)