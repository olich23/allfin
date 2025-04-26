import aiohttp

OPENROUTER_API_KEY = "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"

async def parse_finance_message(text):
    prompt = f"""
Ты — ассистент по финансовому учету digital-агентства.
Твоя задача — из текста пользователя извлечь параметры:

- total: сумма (число без валюты)
- project_name: название проекта
- category_name: название статьи расходов
- plan_paid_date: плановая дата оплаты (формат YYYY-MM-DD или пусто, если не указано)

Отвечай строго в формате JSON.

Текст: \"{text}\"
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-telegram-bot.com",  # можно заменить на свой сайт или оставить так
        "X-Title": "FinanceBot"
    }

    body = {
        "model": "openrouter/mistral-7b",  # легкая и быстрая модель, можно поменять
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    url = "https://openrouter.ai/api/v1/chat/completions"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as resp:
            data = await resp.json()
            try:
                response_text = data["choices"][0]["message"]["content"]
                parsed = eval(response_text)  # можно заменить на json.loads для безопасности
                # Здесь тебе нужно будет сопоставить project_name и category_name с ID
                # Пока возвращаем тестовые ID для примера
                return {
                    "name": f"{parsed.get('category_name', 'Расход')} для {parsed.get('project_name', 'Проект')}",
                    "total": parsed.get("total", 0),
                    "project_id": 99,   # Здесь надо будет маппинг названия проекта -> project_id
                    "category_id": 3058, # Здесь надо будет маппинг названия статьи -> category_id
                    "org_account_id": 20,
                    "currency_id": 99,
                    "plan_paid_date": parsed.get("plan_paid_date", None),
                    "accrual_month": None
                }
            except Exception as e:
                return {"error": f"Ошибка разбора ответа: {e}, ответ: {data}"}
