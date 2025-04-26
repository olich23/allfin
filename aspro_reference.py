import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module/"

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

def get_projects():
    url = BASE_URL + "project/project/list"
    payload = {
        "api_key": API_KEY,
    }
    response = requests.post(url, headers=HEADERS, data=payload)
    try:
        result = response.json()
        projects = result.get("response", [])
        # Вернем удобный список для поиска: [{"id": ..., "name": ...}, ...]
        return [{"id": proj["id"], "name": proj["name"]} for proj in projects]
    except Exception as e:
        print(f"Ошибка при получении проектов: {e}")
        return []

def get_categories():
    url = BASE_URL + "fin/category/list"
    payload = {
        "api_key": API_KEY,
    }
    response = requests.post(url, headers=HEADERS, data=payload)
    try:
        result = response.json()
        categories = result.get("response", [])
        return [{"id": cat["id"], "name": cat["name"]} for cat in categories]
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return []
