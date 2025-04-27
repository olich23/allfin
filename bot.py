from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense, create_income
from aspro_reference import (
    load_projects,
    load_categories,
    find_project_id,
    find_category_id,
)
from rapidfuzz import process
import datetime

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

async def load_references():
    projects = await load_projects()
    expense_cats, income_cats = await load_categories()  # теперь возвращает два списка
    print("DEBUG: Projects loaded:", [p["name"] for p in projects])
    print("DEBUG: Expense categories loaded:", [c["name"] for c in expense_cats])
    print("DEBUG: Income categories loaded:", [c["name"] for c in income_cats])
    return projects, expense_cats, income_cats

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed = await parse_finance_message(text)
    if parsed.get("error"):
        return await update.message.reply_text(parsed["error"])

    direction = parsed.get("direction", "expense")  # "expense" или "income"
    cat_name  = parsed["category_name"]
    proj_name = parsed["project_name"]
    total     = parsed["total"]

    # Находим проект
    proj_id = await find_project_id(context.bot_data['projects'], proj_name)
    if not proj_id:
        sugg = suggest_similar_projects(context.bot_data['projects'], proj_name)
        msg = (
            f"Проект '{proj_name}' не найден. "
            + (f"Возможно, вы имели в виду: {', '.join(sugg)}" if sugg else "")
        )
        return await update.message.reply_text(msg)

    # Выбираем нужный список категорий
    cats = (
        context.bot_data['expense_categories']
        if direction == "expense"
        else context.bot_data['income_categories']
    )

    # Ищем ID категории
    cat_id = await find_category_id(cats, cat_name)
    if not cat_id:
        sugg = suggest_similar_categories(cats, cat_name)
        what = "расходов" if direction == "expense" else "доходов"
        msg = (
            f"Статья {what} '{cat_name}' не найдена. "
            + (f"Возможно, вы имели в виду: {', '.join(sugg)}" if sugg else "")
        )
        return await update.message.reply_text(msg)

    # Параметры по умолчанию
    org_account_id = 20
    currency_id    = 99
    plan_date      = parsed.get("plan_paid_date",
                        datetime.date.today().strftime("%Y-%m-%d"))
    accrual_month  = datetime.date.today().strftime("%Y-%m")

    # Создаём запись в Aspro
    if direction == "expense":
        result = create_expense(
            name=f"{cat_name} для {proj_name}",
            total=total,
            project_id=proj_id,
            category_id=cat_id,
            plan_paid_date=plan_date,
            accrual_month=accrual_month,
            org_account_id=org_account_id,
            currency_id=currency_id,
        )
    else:
        result = create_income(
            name=f"{cat_name} для {proj_name}",
            total=total,
            project_id=proj_id,
            category_id=cat_id,
            plan_paid_date=plan_date,
            accrual_month=accrual_month,
            org_account_id=org_account_id,
            currency_id=currency_id,
        )

    await update.message.reply_text(f"Ответ от Aspro: {result}")

def suggest_similar_projects(projects, query, max_suggestions=5):
    names = [p["name"] for p in projects]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]

def suggest_similar_categories(cats, query, max_suggestions=5):
    names = [c["name"] for c in cats]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]

if __name__ == "__main__":
    import asyncio

    async def main():
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        projects, expense_cats, income_cats = await load_references()
        app.bot_data['projects']           = projects
        app.bot_data['expense_categories'] = expense_cats
        app.bot_data['income_categories']  = income_cats

        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

        print("Запущен бот. Ожидаю сообщений…")
        await app.run_polling()

    asyncio.run(main())
