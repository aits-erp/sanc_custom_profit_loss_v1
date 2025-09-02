# Copyright (c) 2025, pankaj and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import get_data, get_period_list

def execute(filters=None):
    if not filters.get("period_start_date") or not filters.get("period_end_date"):
        frappe.throw(_("From Date and To Date are mandatory."))

    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    currency = filters.presentation_currency or frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )

    # --- Profit & Loss Data ---
    income = get_data(filters.company, "Income", "Credit", period_list,
                      filters=filters, accumulated_values=filters.accumulated_values)
    expense = get_data(filters.company, "Expense", "Debit", period_list,
                       filters=filters, accumulated_values=filters.accumulated_values)

    # --- Totals only for top-level accounts ---
    total_income = sum(flt(row.get("total", 0)) for row in income if row.get("indent") == 0)
    total_expense = sum(flt(row.get("total", 0)) for row in expense if row.get("indent") == 0)

    # Net Profit/Loss
    net_profit_loss_amount = total_income - total_expense
    net_profit_loss = {
        "account_name": _("Net Profit / Loss"),
        "account": "Net P&L",
        "parent_account": "PL Expense Root",
        "total": net_profit_loss_amount,
        "indent": 1,  # visually under Expenses
        "is_group": 0
    }

    # --- Columns ---
    columns = [
        {"label": _("Expense"), "fieldname": "expense_account", "fieldtype": "Data", "width": 300},
        {"label": _("Amount"), "fieldname": "expense_amount", "fieldtype": "Currency", "options": currency, "width": 150},
        {"label": _("Income"), "fieldname": "income_account", "fieldtype": "Data", "width": 300},
        {"label": _("Amount"), "fieldname": "income_amount", "fieldtype": "Currency", "options": currency, "width": 150},
    ]

    data = []

    # --- Profit & Loss Roots ---
    data.append({
        "expense_account": _("Profit & Loss (Expenses)"),
        "account": "PL Expense Root",
        "parent_account": None,
        "indent": 0,
        "is_group": 1,
        "show": 1
    })

    data.append({
        "income_account": _("Profit & Loss (Income)"),
        "account": "PL Income Root",
        "parent_account": None,
        "indent": 0,
        "is_group": 1,
        "show": 1
    })

    # Expense hierarchy
    for row in expense:
        data.append({
            "expense_account": row.get("account_name"),
            "expense_amount": row.get("total"),
            "account": row.get("account"),
            "parent_account": row.get("parent_account") or "PL Expense Root",
            "indent": row.get("indent", 1),
            "is_group": row.get("is_group", 0)
        })

    # Income hierarchy
    for row in income:
        data.append({
            "income_account": row.get("account_name"),
            "income_amount": row.get("total"),
            "account": row.get("account"),
            "parent_account": row.get("parent_account") or "PL Income Root",
            "indent": row.get("indent", 1),
            "is_group": row.get("is_group", 0)
        })

    # Net Profit / Loss row (bold + indented)
    data.append({
        "expense_account": net_profit_loss.get("account_name"),
        "expense_amount": net_profit_loss.get("total"),
        "account": net_profit_loss.get("account"),
        "parent_account": "PL Expense Root",
        "indent": 1,
        "is_group": 0,
        "bold": 1
    })

    # Totals row for top-level accounts
    data.append({
        "expense_account": _("Total Expenses"),
        "expense_amount": total_expense,
        "income_account": _("Total Income"),
        "income_amount": total_income,
        "indent": 0,
        "is_group": 0,
        "bold": 1  # optional: makes totals row bold
    })

    return columns, data


