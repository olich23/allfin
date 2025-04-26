import asyncio
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense
from aspro_reference import load_projects, load_categories, find_project_id, find_category_id

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

async def main():
    # Загружаем справочники
    projects_list = await load_projects()
    categories_list = await load_categories()

    print("Загруженные проекты:")
    for p in projects_list:
        print(f"- {p['id']}: {p['name']}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        parsed_data = await parse_finance_message(text)

        if parsed_data.get("error"):
            await update.message.reply_text(parsed_data["error"])
            return

        name = f"{parsed_data['category_name']} для {parsed_data['project_name']}"
        total = parsed_data["total"]

        project_id = find_project_id(projects_list, parsed_data["project_name"])
        if not project_id:
            await update.message.reply_text(f"Проект '{parsed_data['project_name']}' не найден в системе.")
            return

        category_id = find_category_id(categories_list, parsed_data["category_name"])
        if not category_id:
            await update.message.reply_text(f"Статья расходов '{parsed_data['category_name']}' не найдена в системе.")
            return

        org_account_id = 20  # фиксированное значение
        currency_id = 99     # фиксированное значение

        plan_paid_date = parsed_data.get("plan_paid_date", datetime.date.today().strftime("%Y-%m-%d"))
        accrual_month = datetime.date.today().strftime("%Y-%m")

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

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
