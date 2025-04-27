import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module/st"

projects_list = []
expense_categories_list = []
income_categories_list = []

# Функция для загрузки проектов из Aspro
async def load_projects():
    global projects_list
    url = f"{BASE_URL}/projects/list?api_key={API_KEY}"
    response = requests.get(url)
    print(f"Ответ сервера по проектам: {response.text}")
    if response.status_code == 200:
        try:
            data = response.json()
            projects_list = data.get("response", {}).get("items", [])
            print(f"Загруженные проекты: {', '.join([p['name'] for p in projects_list])}")
        except Exception as e:
            print(f"Ошибка при обработке данных о проектах: {e}")
    else:
        print(f"Ошибка при получении проектов: {response.status_code} {response.text}")
    return projects_list

# Функция для загрузки статей расходов
async def load_expense_categories():
    global expense_categories_list
    url = f"{BASE_URL}/outcome_categories/list?api_key={API_KEY}"
    response = requests.get(url)
    print(f"Ответ сервера по статьям расходов: {response.text}")
    if response.status_code == 200:
        try:
            data = response.json()
            expense_categories_list = data.get("response", {}).get("items", [])
            print(f"Загруженные статьи расходов: {', '.join([c['name'] for c in expense_categories_list])}")
        except Exception as e:
            print(f"Ошибка при обработке статей расходов: {e}")
    else:
        print(f"Ошибка при получении статей расходов: {response.status_code} {response.text}")
    return expense_categories_list

# Функция для загрузки статей доходов
async def load_income_categories():
    global income_categories_list
    url = f"{BASE_URL}/income_categories/list?api_key={API_KEY}"
    response = requests.get(url)
    print(f"Ответ сервера по статьям доходов: {response.text}")
    if response.status_code == 200:
        try:
            data = response.json()
            income_categories_list = data.get("response", {}).get("items", [])
            print(f"Загруженные статьи доходов: {', '.join([c['name'] for c in income_categories_list])}")
        except Exception as e:
            print(f"Ошибка при обработке статей доходов: {e}")
    else:
        print(f"Ошибка при получении статей доходов: {response.status_code} {response.text}")
    return income_categories_list

# Функция поиска project_id по названию проекта
async def find_project_id(projects, project_name):
    if not project_name:
        return None
    project_name = project_name.lower().strip()
    for project in projects:
        name_in_list = project.get("name", "").lower().strip()
        if project_name in name_in_list or name_in_list in project_name:
            return project.get("id")
    return None

# Функция поиска category_id по названию категории расходов
async def find_expense_category_id(categories, category_name):
    if not category_name:
        return None
    category_name = category_name.lower().strip()
    for category in categories:
        name_in_list = category.get("name", "").lower().strip()
        if category_name in name_in_list or name_in_list in category_name:
            return category.get("id")
    return None

# Функция поиска category_id по названию категории доходов
async def find_income_category_id(categories, category_name):
    if not category_name:
        return None
    category_name = category_name.lower().strip()
    for category in categories:
        name_in_list = category.get("name", "").lower().strip()
        if category_name in name_in_list or name_in_list in category_name:
            return category.get("id")
    return None
