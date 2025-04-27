from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense, create_income
from aspro_reference import (
    load_projects,
    load_expense_categories,
    load_income_categories,
    find_project_id,
    find_expense_category_id,
    find_income_category_id,
)
from rapidfuzz import process
import datetime

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

async def load_references():
    projects = await load_projects()
    expense_cats = await load_expense_categories()
    income_cats = await load_income_categories()
    return projects, expense_cats, income_cats

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed = await parse_finance_message(text)

    # Ошибка парсинга
    if parsed.get("error"):
        await update.message.reply_text(parsed["error"])
        return

    rec_type = parsed.get("type")  # "expense" или "income"
    project_name = parsed["project_name"]
    cat_name = parsed["category_name"]
    total = parsed["total"]

    # Поиск проекта
    project_id = await find_project_id(context.bot_data['projects'], project_name)
    if not project_id:
        suggestions = suggest_similar_projects(context.bot_data['projects'], project_name)
        if suggestions:
            await update.message.reply_text(
                f"Проект '{project_name}' не найден. Возможно, вы имели в виду: {', '.join(suggestions)}"
            )
        else:
            await update.message.reply_text(f"Проект '{project_name}' не найден в системе.")
        return

    # Поиск категории
    if rec_type == "expense":
        cat_id = await find_expense_category_id(context.bot_data['expense_categories'], cat_name)
    else:
        cat_id = await find_income_category_id(context.bot_data['income_categories'], cat_name)

    if not cat_id:
        if rec_type == "expense":
            suggestions = suggest_similar_categories(context.bot_data['expense_categories'], cat_name)
            label = "статья расходов"
        else:
            suggestions = suggest_similar_categories(context.bot_data['income_categories'], cat_name)
            label = "статья доходов"
        if suggestions:
            await update.message.reply_text(
                f"{label.title()} '{cat_name}' не найдена. Возможно, вы имели в виду: {', '.join(suggestions)}"
            )
        else:
            await update.message.reply_text(f"{label.title()} '{cat_name}' не найдена в системе.")
        return

    # Параметры для API
    name = f"{cat_name} для {project_name}"
    plan_paid_date = parsed.get("plan_paid_date", datetime.date.today().strftime("%Y-%m-%d"))
    accrual_month = parsed.get("accrual_month", datetime.date.today().strftime("%Y-%m"))
    org_account_id = 20
    currency_id = 99

    # Создание записи в Aspro
    if rec_type == "expense":
        result = create_expense(
            name=name,
            total=total,
            project_id=project_id,
            category_id=cat_id,
            plan_paid_date=plan_paid_date,
            accrual_month=accrual_month,
            org_account_id=org_account_id,
            currency_id=currency_id,
        )
    else:
        result = create_income(
            name=name,
            total=total,
            project_id=project_id,
            category_id=cat_id,
            plan_paid_date=plan_paid_date,
            accrual_month=accrual_month,
            org_account_id=org_account_id,
            currency_id=currency_id,
        )

    await update.message.reply_text(f"Ответ от Aspro: {result}")

# Подсказки для названий

def suggest_similar_projects(list_, query, max_suggestions=5):
    names = [p["name"] for p in list_]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]

# Используем для обеих категорий

def suggest_similar_categories(list_, query, max_suggestions=5):
    names = [c["name"] for c in list_]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]

if __name__ == "__main__":
    import asyncio

    async def main():
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        projects, expense_categories, income_categories = await load_references()
        app.bot_data['projects'] = projects
        app.bot_data['expense_categories'] = expense_categories
        app.bot_data['income_categories'] = income_categories

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Загруженные проекты:")
        for p in projects:
            print(f"- {p['id']}: {p['name']}")

        print("Загруженные статьи расходов:", [c['name'] for c in expense_categories])
        print("Загруженные статьи доходов:", [c['name'] for c in income_categories])

        await app.run_polling()

    asyncio.run(main())
