import aiohttp
import json

OPENROUTER_API_KEY = "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"

async def parse_finance_message(text):
    prompt = f"""
Ты — ассистент по финансовому учету digital-агентства.

Твоя задача:
Из текста пользователя извлеки ТОЛЬКО следующие поля:
- total (сумма, целое число без знаков валют)
- project_name (название проекта, строка)
- category_name (название статьи расходов, строка)
- plan_paid_date (дата оплаты в формате YYYY-MM-DD, или null, если дата не указана)

Правила:
- Ответ ДОЛЖЕН быть только чистым JSON без комментариев.
- Нельзя вставлять никакой PHP-код, объяснения или дополнительный текст.
- Если дата не указана пользователем — ставь null.

Пример правильного ответа:
{{
    "total": 15000,
    "project_name": "SEO Петрова",
    "category_name": "реклама",
    "plan_paid_date": null
}}

Текст пользователя: \"{text}\"
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-telegram-bot.com",
        "X-Title": "FinanceBot"
    }

    body = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    url = "https://openrouter.ai/api/v1/chat/completions"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as resp:
            if resp.status != 200:
                error = await resp.text()
                return {"error": f"Ошибка обращения к ИИ: {error}"}
            data = await resp.json()
            try:
                response_text = data["choices"][0]["message"]["content"]
                parsed = json.loads(response_text)
                return parsed
            except Exception as e:
                return {"error": f"Ошибка разбора ответа: {e}, ответ: {data}"}

