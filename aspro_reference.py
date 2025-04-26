import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module/st"

projects_list = []
categories_list = []

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

# Функция загрузки категорий расходов
async def load_categories():
    global categories_list
    url = f"{BASE_URL}/outcome_categories/list?api_key={API_KEY}"
    response = requests.get(url)
    print(f"Ответ сервера по категориям: {response.text}")
    if response.status_code == 200:
        try:
            data = response.json()
            categories_list = data.get("response", {}).get("items", [])
            print(f"Загруженные категории: {', '.join([c['name'] for c in categories_list])}")
        except Exception as e:
            print(f"Ошибка при обработке данных о категориях: {e}")
    else:
        print(f"Ошибка при получении категорий: {response.status_code} {response.text}")

# Функция поиска category_id по названию категории
async def find_category_id(categories, category_name):
    if not category_name:
        return None
    category_name = category_name.lower().strip()
    for category in categories:
        name_in_list = category.get("name", "").lower().strip()
        if category_name in name_in_list or name_in_list in category_name:
            return category.get("id")
    return None
