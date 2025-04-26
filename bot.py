from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense
from aspro_reference import get_projects, get_categories, find_project_id, find_category_id
import datetime

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

# При старте загрузим справочники
projects_list = get_projects()
categories_list = get_categories()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed_data = await parse_finance_message(text)

    if parsed_data.get("error"):
        await update.message.reply_text(parsed_data["error"])
        return

    # Собираем название расхода из категории и проекта
    name = f"{parsed_data['category_name']} для {parsed_data['project_name']}"
    total = parsed_data["total"]

    # Поиск project_id и category_id через справочники
    project_id = find_project_id(projects_list, parsed_data["project_name"])
    if not project_id:
        await update.message.reply_text(f"Проект '{parsed_data['project_name']}' не найден в системе.")
        return

    category_id = find_category_id(categories_list, parsed_data["category_name"])
    if not category_id:
        await update.message.reply_text(f"Статья расходов '{parsed_data['category_name']}' не найдена в системе.")
        return

    org_account_id = 20  # фиксируем на старте, потом можно будет брать динамически
    currency_id = 99     # фиксируем на старте, потом можно будет брать динамически

    plan_paid_date = parsed_data.get("plan_paid_date", datetime.date.today().strftime("%Y-%m-%d"))
    accrual_month = datetime.date.today().strftime("%Y-%m")  # по умолчанию текущий месяц

    result = create_expense(
        name=name,
        total=total,
        project_id=project_id,
        category_id=category_id,
        plan_paid_date=plan_paid_date,
        accrual_month=accrual_month,
        org_account_id=org_account_id,
        currency_id=currency_id,
    )

    await update.message.reply_text(f"Ответ от Aspro: {result}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
