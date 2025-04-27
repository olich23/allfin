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
import asyncio

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"


# ---------- справочники ----------
async def load_references() -> tuple[list, list, list]:
    projects      = await load_projects()
    expense_cats  = await load_expense_categories()
    income_cats   = await load_income_categories()
    return projects, expense_cats, income_cats


# ---------- обработка входящих сообщений ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text   = update.message.text
    parsed = await parse_finance_message(text)

    # Ошибка парсинга
    if parsed.get("error"):
        await update.message.reply_text(parsed["error"])
        return

    rec_type     = parsed["type"]           # "expense" | "income"
    project_name = parsed["project_name"]
    cat_name     = parsed["category_name"]
    total        = parsed["total"]

    # ---- проект ----
    project_id = find_project_id(context.bot_data["projects"], project_name)
    if not project_id:
        suggestions = suggest_similar_projects(context.bot_data["projects"], project_name)
        msg = (
            f"Проект «{project_name}» не найден."
            + (f" Возможно, вы имели в виду: {', '.join(suggestions)}" if suggestions else "")
        )
        await update.message.reply_text(msg)
        return

    # ---- категория ----
    if rec_type == "expense":
        cat_id = find_expense_category_id(context.bot_data["expense_categories"], cat_name)
        label  = "статья расходов"
        cats   = context.bot_data["expense_categories"]
    else:
        cat_id = find_income_category_id(context.bot_data["income_categories"], cat_name)
        label  = "статья доходов"
        cats   = context.bot_data["income_categories"]

    if not cat_id:
        suggestions = suggest_similar_categories(cats, cat_name)
        msg = (
            f"{label.title()} «{cat_name}» не найдена."
            + (f" Возможно, вы имели в виду: {', '.join(suggestions)}" if suggestions else "")
        )
        await update.message.reply_text(msg)
        return

    # ---- параметры записи ----
    name           = f"{cat_name} для {project_name}"
    plan_paid_date = parsed.get("plan_paid_date", datetime.date.today().strftime("%Y-%m-%d"))
    accrual_month  = parsed.get("accrual_month",  datetime.date.today().strftime("%Y-%m"))
    org_account_id = 20
    currency_id    = 99

    # ---- вызов API ----
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

    await update.message.reply_text(f"Ответ от Aspro:\n{result}")


# ---------- подсказки ----------
def suggest_similar_projects(list_, query, max_suggestions=5):
    names   = [p["name"] for p in list_]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]


def suggest_similar_categories(list_, query, max_suggestions=5):
    names   = [c["name"] for c in list_]
    matches = process.extract(query, names, limit=max_suggestions, score_cutoff=50)
    return [m[0] for m in matches]


# ---------- запуск ----------
if __name__ == "__main__":
    async def main():
        # загружаем справочники
        projects, expense_cats, income_cats = await load_references()

        # инициализируем бота
        app = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .build()
        )

        # сохраняем справочники в контексте
        app.bot_data["projects"]           = projects
        app.bot_data["expense_categories"] = expense_cats
        app.bot_data["income_categories"]  = income_cats

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # выводим содержимое справочников
        print("Загруженные проекты:")
        for p in projects:
            print(f"- {p['id']}: {p['name']}")
        print("Загруженные статьи расходов:", [c["name"] for c in expense_cats])
        print("Загруженные статьи доходов:", [c["name"] for c in income_cats])

        await app.run_polling()

    # в некоторых окружениях asyncio.run может конфликтовать с уже
    # запущенным циклом – защитимся try/except.
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            # если цикл уже запущен (например, Jupyter) – используем create_task
            loop = asyncio.get_running_loop()
            loop.create_task(main())
        else:
            raise
