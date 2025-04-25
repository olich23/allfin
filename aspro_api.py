import requests

API_KEY = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL = "https://pirus.aspro.cloud/api/v1/module/fin/plan_money/create"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
manager_id = 304332

def create_expense(name, total, project_id, category_id, plan_paid_date, accrual_month, org_account_id, currency_id):
    payload = {
        "api_key": API_KEY,
        "name": name,
        "plan_paid_date": plan_paid_date,
        "accrual_month": accrual_month,
        "category_id": category_id,
        "total": total,
        "org_account_id": org_account_id,
        "project_id": project_id,
        "currency_id": currency_id,
        "manager_id": manager_id,
        "type": 20
    }
    response = requests.post(BASE_URL, headers=HEADERS, data=payload)
    try:
        return response.json()
    except Exception:
        return response.text
