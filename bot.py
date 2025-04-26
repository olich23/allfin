from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nlp import parse_finance_message
from aspro_api import create_expense
from aspro_reference import load_projects, load_categories, find_project_id, find_category_id
from rapidfuzz import process
import datetime

BOT_TOKEN = "7769240179:AAHPT10IML3CezoYu71h3sbYmaXsxL9MMPU"

async def load_references():
    projects = await load_projects()
    categories = await load_categories()
    print("DEBUG: Projects loaded:", projects)
    print("DEBUG: Categories loaded:", categories)
    return projects, categories

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parsed_data = await parse_finance_message(text)

    if parsed_data.get("error"):
        await update.message.reply_text(parsed_data["error"])
        return

    name = f"{parsed_data['category_name']} для {parsed_data['project_name']}"
    total = parsed_data["total"]

    project_id = find_project_id(context.bot_data['projects_list'], parsed_data["project_name"])
    if not project_id:
        suggestions = suggest_similar_projects(context.bot_data['projects_list'], parsed_data["project_name"])
        if suggestions:
            await update.message.reply_text(f"Проект '{parsed_data['project_name']}' не найден. Возможно, вы имели в виду: {', '.join(suggestions)}")
        else:
            await update.message.reply_text(f"Проект '{parsed_data['project_name']}' не найден в системе.")
        return

    category_id = find_category_id(context.bot_data['categories_list'], parsed_data["category_name"])
    if not category_id:
        suggestions = suggest_similar_categories(context.bot_data['categories_list'], parsed_data["category_name"])
        if suggestions:
            await update.message.reply_text(f"Статья расходов '{parsed_data['category_name']}' не найдена. Возможно, вы имели в виду: {', '.join(suggestions)}")
        else:
            await update.message.reply_text(f"Статья расходов '{parsed_data['category_name']}' не найдена в системе.")
        return

    org_account_id = 20
    currency_id = 99

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

def suggest_similar_projects(projects_list, query, max_suggestions=5):
    project_names = [p["name"] for p in projects_list]
    matches = process.extract(query, project_names, limit=max_suggestions, score_cutoff=50)
    return [match[0] for match in matches]

def suggest_similar_categories(categories_list, query, max_suggestions=5):
    category_names = [c["name"] for c in categories_list]
    matches = process.extract(query, category_names, limit=max_suggestions, score_cutoff=50)
    return [match[0] for match in matches]

if __name__ == "__main__":
    import asyncio

    async def main():
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        projects_list, categories_list = await load_references()
        app.bot_data['projects_list'] = projects_list
        app.bot_data['categories_list'] = categories_list

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Загруженные проекты:")
        for p in projects_list:
            print(f"- {p['id']}: {p['name']}")

        await app.run_polling()

    asyncio.run(main())
