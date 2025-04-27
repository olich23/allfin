import requests, asyncio

API_KEY   = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"

# разные модули в REST-пути
BASE_ST  = "https://pirus.aspro.cloud/api/v1/module/st"   # проекты
BASE_FIN = "https://pirus.aspro.cloud/api/v1/module/fin"  # финансы (статьи)

projects_list         : list[dict] = []
expense_categories_list: list[dict] = []
income_categories_list : list[dict] = []


# ------------ util ---------------
def _get(url: str) -> list[dict]:
    """Общий геттер: вернёт items [] либо [] при ошибке, выведет debug."""
    resp = requests.get(url)
    print("DEBUG →", url, "→", resp.text[:120])
    if resp.ok:
        try:
            return resp.json().get("response", {}).get("items", [])
        except Exception as e:
            print("Ошибка обработки JSON:", e)
    return []


# ---------- загрузка справочников ----------
async def load_projects() -> list[dict]:
    global projects_list
    projects_list = _get(f"{BASE_ST}/projects/list?api_key={API_KEY}")
    print("Загруженные проекты:",
          ", ".join(p["name"] for p in projects_list) or "—")
    return projects_list


async def load_expense_categories() -> list[dict]:
    global expense_categories_list
    expense_categories_list = _get(
        f"{BASE_FIN}/outcome_categories/list?api_key={API_KEY}"
    )
    print("Загруженные статьи расходов:",
          ", ".join(c["name"] for c in expense_categories_list) or "—")
    return expense_categories_list


async def load_income_categories() -> list[dict]:
    global income_categories_list
    income_categories_list = _get(
        f"{BASE_FIN}/income_categories/list?api_key={API_KEY}"
    )
    print("Загруженные статьи доходов:",
          ", ".join(c["name"] for c in income_categories_list) or "—")
    return income_categories_list


# ------------- поиск ID -------------
def _find_id(items: list[dict], name: str) -> int | None:
    if not name:
        return None
    name = name.lower().strip()
    for it in items:
        val = it.get("name", "").lower().strip()
        if name in val or val in name:
            return it.get("id")
    return None


def find_project_id(projects: list[dict], project_name: str) -> int | None:
    return _find_id(projects, project_name)


def find_expense_category_id(cats: list[dict], cat_name: str) -> int | None:
    return _find_id(cats, cat_name)


def find_income_category_id(cats: list[dict], cat_name: str) -> int | None:
    return _find_id(cats, cat_name)


# ------------ быстрый самотест -------------
if __name__ == "__main__":
    async def _test():
        await asyncio.gather(
            load_projects(),
            load_expense_categories(),
            load_income_categories()
        )
        print(
            "Всего:", len(projects_list), "проектов |",
            len(expense_categories_list), "расходных |",
            len(income_categories_list), "доходных"
        )
    asyncio.run(_test())
