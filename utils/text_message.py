import logging

logger = logging.getLogger(__name__)


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