from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense
import datetime

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed_data = await parse_finance_message(text)

    if parsed_data.get("error"):
        await update.message.reply_text(parsed_data["error"])
        return

    name = parsed_data["name"]
    total = parsed_data["total"]
    project_id = parsed_data["project_id"]
    category_id = parsed_data["category_id"]
    org_account_id = parsed_data["org_account_id"]
    currency_id = parsed_data["currency_id"]
    
    plan_paid_date = parsed_data.get("plan_paid_date", datetime.date.today().strftime("%Y-%m-%d"))
    accrual_month = parsed_data.get("accrual_month", datetime.date.today().strftime("%Y-%m"))

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
