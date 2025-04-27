import requests

API_KEY   = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
# один и тот же endpoint для расходов и доходов
BASE_URL  = "https://pirus.aspro.cloud/api/v1/module/fin/plan_money/create"
HEADERS   = {"Content-Type": "application/x-www-form-urlencoded"}

# кто «создаёт» запись в Aspro.Cloud
MANAGER_ID = 304332


def _post_plan_money(payload: dict):
    """Вспомогательная обёртка: POST и попытка .json()"""
    response = requests.post(BASE_URL, headers=HEADERS, data=payload)
    try:
        return response.json()
    except Exception:
        return response.text


def create_expense(
    name: str,
    total: float,
    project_id: int,
    category_id: int,
    plan_paid_date: str,
    accrual_month: str,
    org_account_id: int,
    currency_id: int,
):
    """
    Создать *расход* (type = 20) в «План денег».
    """
    payload = {
        "api_key":       API_KEY,
        "name":          name,
        "plan_paid_date": plan_paid_date,
        "accrual_month":  accrual_month,
        "category_id":    category_id,   # статья расходов
        "total":          total,
        "org_account_id": org_account_id,
        "project_id":     project_id,
        "currency_id":    currency_id,
        "manager_id":     MANAGER_ID,
        "type":           20,            # 20 = расход
    }
    return _post_plan_money(payload)


def create_income(
    name: str,
    total: float,
    project_id: int,
    category_id: int,
    plan_paid_date: str,
    accrual_month: str,
    org_account_id: int,
    currency_id: int,
):
    """
    Создать *доход* (type = 10) в «План денег».
    """
    payload = {
        "api_key":       API_KEY,
        "name":          name,
        "plan_paid_date": plan_paid_date,
        "accrual_month":  accrual_month,
        "category_id":    category_id,   # статья ДОХОДОВ!
        "total":          total,
        "org_account_id": org_account_id,
        "project_id":     project_id,
        "currency_id":    currency_id,
        "manager_id":     MANAGER_ID,
        "type":           10,            # 10 = доход
    }
    return _post_plan_money(payload)
