import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module/"

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

def get_projects():
    """Получить список проектов из Aspro Cloud"""
    url = BASE_URL + "project/project/list"
    payload = {
        "api_key": API_KEY,
    }
    try:
        response = requests.post(url, headers=HEADERS, data=payload)
        response.raise_for_status()
        result = response.json()
        projects = result.get("response", [])
        return [{"id": proj["id"], "name": proj["name"]} for proj in projects]
    except Exception as e:
        print(f"Ошибка при получении проектов: {e}")
        return []

def get_categories():
    """Получить список категорий расходов из Aspro Cloud"""
    url = BASE_URL + "fin/category/list"
    payload = {
        "api_key": API_KEY,
    }
    try:
        response = requests.post(url, headers=HEADERS, data=payload)
        response.raise_for_status()
        result = response.json()
        categories = result.get("response", [])
        return [{"id": cat["id"], "name": cat["name"]} for cat in categories]
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return []

def normalize_name(name):
    """Приводит название к единому виду: убирает пробелы, приводит к нижнему регистру"""
    return name.replace(" ", "").lower() if name else ""

def find_project_id(projects_list, name_to_find):
    """Ищет project_id по нормализованному названию проекта"""
    if not name_to_find:
        return None
    normalized_name_to_find = normalize_name(name_to_find)
    for project in projects_list:
        if normalized_name_to_find in normalize_name(project["name"]):
            return project["id"]
    return None

def find_category_id(categories_list, name_to_find):
    """Ищет category_id по нормализованному названию статьи расходов"""
    if not name_to_find:
        return None
    normalized_name_to_find = normalize_name(name_to_find)
    for category in categories_list:
        if normalized_name_to_find in normalize_name(category["name"]):
            return category["id"]
    return None

