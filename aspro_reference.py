import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module"

# Глобальные переменные для кеширования
projects_list = []
expense_categories_list = []
income_categories_list = []

# Функция для загрузки списка проектов
async def load_projects():
    global projects_list
    url = f"{BASE_URL}/st/project/list?api_key={API_KEY}"
    response = requests.get(url)
    print(f"Ответ сервера по проектам: {response.text}")
    if response.status_code == 200:
        try:
            data = response.json()
            projects_list = data.get("response", {}).get("items", [])
            names = [p.get("name", "") for p in projects_list]
            print(f"Загруженные проекты: {', '.join(names)}")
        except Exception as e:
            print(f"Ошибка при обработке данных о проектах: {e}")
    else:
        print(f"Ошибка при получении проектов: {response.status_code} {response.text}")
    return projects_list

# Функция загрузки статей расходов и доходов
async def load_categories():
    global expense_categories_list, income_categories_list

    # Статьи расходов (type = 10)
    url_out = (
        f"{BASE_URL}/fin/category/list"
        f"?api_key={API_KEY}"
        f"&filter[type]=10"
    )
    resp_out = requests.get(url_out)
    print(f"Ответ сервера по статьям расходов: {resp_out.text}")
    if resp_out.status_code == 200:
        try:
            items = resp_out.json().get("response", {}).get("items", [])
            expense_categories_list = [
                {"id": c["id"], "name": c["name"]} for c in items
            ]
        except Exception as e:
            print(f"Ошибка при обработке статей расходов: {e}")
    else:
        print(f"Ошибка при получении статей расходов: {resp_out.status_code} {resp_out.text}")

    # Статьи доходов (type = 20)
    url_in = (
        f"{BASE_URL}/fin/category/list"
        f"?api_key={API_KEY}"
        f"&filter[type]=20"
    )
    resp_in = requests.get(url_in)
    print(f"Ответ сервера по статьям доходов: {resp_in.text}")
    if resp_in.status_code == 200:
        try:
            items = resp_in.json().get("response", {}).get("items", [])
            income_categories_list = [
                {"id": c["id"], "name": c["name"]} for c in items
            ]
        except Exception as e:
            print(f"Ошибка при обработке статей доходов: {e}")
    else:
        print(f"Ошибка при получении статей доходов: {resp_in.status_code} {resp_in.text}")

    print(
        f"Загруженные статьи расходов: {', '.join([c['name'] for c in expense_categories_list])}"
    )
    print(
        f"Загруженные статьи доходов: {', '.join([c['name'] for c in income_categories_list])}"
    )
    return expense_categories_list, income_categories_list

# Поиск project_id по названию проекта
async def find_project_id(projects, project_name):
    if not project_name:
        return None
    q = project_name.lower().strip()
    for p in projects:
        name = p.get("name", "").lower().strip()
        if q in name or name in q:
            return p.get("id")
    return None

# Поиск category_id по названию статьи расходов/доходов
async def find_category_id(categories, category_name):
    if not category_name:
        return None
    q = category_name.lower().strip()
    for c in categories:
        name = c.get("name", "").lower().strip()
        if q in name or name in q:
            return c.get("id")
    return None
