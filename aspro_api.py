# aspro_api.py
from __future__ import annotations

import requests
from datetime import datetime
from typing import Any, Tuple

# --- конфигурация -----------------------------------------------------------
API_KEY     = "WFhISk9wZVBPamVmd3U2TTVaR0ZLQW9uTk90WWJIeTdfMTAxNTc3"
BASE_URL    = "https://pirus.aspro.cloud/api/v1/module/fin/plan_money/create"
HEADERS     = {"Content-Type": "application/x-www-form-urlencoded"}
MANAGER_ID  = 304332
# -----------------------------------------------------------------------------


def _create_plan_money(
    *,
    name: str,
    total: float | int,
    type_code: int,               # 10 — доход, 20 — расход
    category_id: int,
    project_id: int,
    plan_paid_date: str,
    accrual_month: str,
    org_account_id: int,
    currency_id: int,
    api_key: str = API_KEY,
    manager_id: int = MANAGER_ID,
    base_url: str = BASE_URL,
) -> Tuple[bool, Any]:
    """
    Базовая функция создания записи «План денег».
    Возвращает (ok, data) - где ok — bool успеха, data — json|str ответа.
    """

    # --- валидация простейших параметров ------------------------------------
    try:
        _ = float(total)
    except (TypeError, ValueError):
        raise ValueError("«total» должен быть числом")

    # проверки форматов дат (YYYY-MM-DD / YYYY-MM)
    for val, fmt in ((plan_paid_date, "%Y-%m-%d"), (accrual_month, "%Y-%m")):
        try:
            datetime.strptime(val, fmt)
        except ValueError:
            raise ValueError(f"Неверный формат даты: {val} (ожидался {fmt})")
    # ------------------------------------------------------------------------

    payload = {
        "api_key":        api_key,
        "name":           name,
        "plan_paid_date": plan_paid_date,
        "accrual_month":  accrual_month,
        "category_id":    category_id,
        "total":          total,
        "org_account_id": org_account_id,
        "project_id":     project_id,
        "currency_id":    currency_id,
        "manager_id":     manager_id,
        "type":           type_code,
    }

    resp = requests.post(base_url, headers=HEADERS, data=payload)
    try:
        data = resp.json()
    except Exception:            # not json → вернём сырой текст
        data = resp.text

    ok = resp.ok and isinstance(data, dict) and "error" not in data
    return ok, data


# ------------------------- публичные обёртки --------------------------------
def create_expense(**kwargs) -> Tuple[bool, Any]:
    """Создать *расход* (type = 20)"""
    return _create_plan_money(type_code=20, **kwargs)


def create_income(**kwargs) -> Tuple[bool, Any]:
    """Создать *доход* (type = 10)"""
    return _create_plan_money(type_code=10, **kwargs)
# ---------------------------------------------------------------------------

