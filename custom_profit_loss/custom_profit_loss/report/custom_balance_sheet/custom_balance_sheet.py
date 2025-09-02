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

    # --- Balance Sheet Data ---
    assets = get_data(filters.company, "Asset", "Debit", period_list,
                      filters=filters, accumulated_values=filters.accumulated_values)
    liabilities = get_data(filters.company, "Liability", "Credit", period_list,
                           filters=filters, accumulated_values=filters.accumulated_values)
    equity = get_data(filters.company, "Equity", "Credit", period_list,
                      filters=filters, accumulated_values=filters.accumulated_values)

    liab_equity = (liabilities or []) + (equity or [])

    # --- Profit & Loss Data ---
    income = get_data(filters.company, "Income", "Credit", period_list,
                      filters=filters, accumulated_values=filters.accumulated_values)
    expense = get_data(filters.company, "Expense", "Debit", period_list,
                       filters=filters, accumulated_values=filters.accumulated_values)

    # --- Totals for top-level accounts only ---
    total_assets = sum(flt(row.get("total", 0)) for row in assets if row.get("indent") == 0)
    total_liab_equity = sum(flt(row.get("total", 0)) for row in liab_equity if row.get("indent") == 0)
    total_income = sum(flt(row.get("total", 0)) for row in income if row.get("indent") == 0)
    total_expense = sum(flt(row.get("total", 0)) for row in expense if row.get("indent") == 0)

    # Calculate Net Profit/Loss
    net_profit_loss = {
        "account_name": _("Net Profit / Loss"),
        "account": "Net P&L",
        "parent_account": "PL Expense Root",
        "total": total_income - total_expense,
        "indent": 0,
        "is_group": 0
    }

    # --- Columns (Assets on right side) ---
    columns = [
        {"label": _("Liabilities & Equity / Profit & Loss"), "fieldname": "liab_account", "fieldtype": "Data", "width": 300},
        {"label": _("Amount"), "fieldname": "liab_amount", "fieldtype": "Currency", "options": currency, "width": 150},
        {"label": _("Assets"), "fieldname": "asset_account", "fieldtype": "Data", "width": 300},
        {"label": _("Amount"), "fieldname": "asset_amount", "fieldtype": "Currency", "options": currency, "width": 150},
    ]

    data = []

    # --- Roots ---
    data.append({
        "liab_account": _("Balance Sheet (Liabilities & Equity)"),
        "account": "Balance Sheet Liabilities Root",
        "parent_account": None,
        "indent": 0,
        "is_group": 1,
        "show": 1
    })
    data.append({
        "asset_account": _("Balance Sheet (Assets)"),
        "account": "Balance Sheet Assets Root",
        "parent_account": None,
        "indent": 0,
        "is_group": 1,
        "show": 1
    })

    # Liabilities & Equity hierarchy
    for row in liab_equity:
        data.append({
            "liab_account": row.get("account_name"),
            "liab_amount": row.get("total"),
            "account": row.get("account"),
            "parent_account": row.get("parent_account") or "Balance Sheet Liabilities Root",
            "indent": row.get("indent", 1),
            "is_group": row.get("is_group", 0)
        })

    # Profit & Loss under Expenses
    data.append({
        "liab_account": net_profit_loss.get("account_name"),
        "liab_amount": net_profit_loss.get("total"),
        "account": net_profit_loss.get("account"),
        "parent_account": "PL Expense Root",
        "indent": 0,
        "is_group": 0,
        "bold": 1
    })

    # Assets hierarchy
    for row in assets:
        data.append({
            "asset_account": row.get("account_name"),
            "asset_amount": row.get("total"),
            "account": row.get("account"),
            "parent_account": row.get("parent_account") or "Balance Sheet Assets Root",
            "indent": row.get("indent", 1),
            "is_group": row.get("is_group", 0)
        })

    # Totals row at the bottom
    data.append({
        "liab_account": _("Total Liabilities & Equity (Top-Level)") + f" + Net P&L",
        "liab_amount": total_liab_equity + net_profit_loss.get("total"),
        "asset_account": _("Total Assets (Top-Level)"),
        "asset_amount": total_assets,
        "indent": 0,
        "is_group": 0
    })

    return columns, data



# import frappe
# from frappe import _
# from frappe.utils import flt
# from erpnext.accounts.report.financial_statements import get_data, get_period_list


# def execute(filters=None):
#     if not filters.get("period_start_date") or not filters.get("period_end_date"):
#         frappe.throw(_("From Date and To Date are mandatory."))

#     period_list = get_period_list(
#         filters.from_fiscal_year,
#         filters.to_fiscal_year,
#         filters.period_start_date,
#         filters.period_end_date,
#         filters.filter_based_on,
#         filters.periodicity,
#         company=filters.company,
#     )

#     currency = filters.presentation_currency or frappe.get_cached_value(
#         "Company", filters.company, "default_currency"
#     )

#     # --- Balance Sheet Data ---
#     assets = get_data(filters.company, "Asset", "Debit", period_list,
#                       filters=filters, accumulated_values=filters.accumulated_values)
#     liabilities = get_data(filters.company, "Liability", "Credit", period_list,
#                            filters=filters, accumulated_values=filters.accumulated_values)
#     equity = get_data(filters.company, "Equity", "Credit", period_list,
#                       filters=filters, accumulated_values=filters.accumulated_values)

#     liab_equity = (liabilities or []) + (equity or [])

#     # --- Profit & Loss Data ---
#     income = get_data(filters.company, "Income", "Credit", period_list,
#                       filters=filters, accumulated_values=filters.accumulated_values)
#     expense = get_data(filters.company, "Expense", "Debit", period_list,
#                        filters=filters, accumulated_values=filters.accumulated_values)

#     # --- Totals for top-level accounts only ---
#     total_assets = sum(flt(row.get("total", 0)) for row in assets if row.get("indent") == 0)
#     total_liab_equity = sum(flt(row.get("total", 0)) for row in liab_equity if row.get("indent") == 0)

#     total_income = sum(flt(row.get("total", 0)) for row in income if row.get("indent") == 0)
#     total_expense = sum(flt(row.get("total", 0)) for row in expense if row.get("indent") == 0)

#     # Calculate Net Profit/Loss
#     net_profit_loss = {
#         "account_name": _("Net Profit / Loss"),
#         "account": "Net P&L",
#         "parent_account": "PL Expense Root",
#         "total": total_income - total_expense,
#         "indent": 0,
#         "is_group": 0
#     }

#     # --- Columns ---
#     columns = [
#         {"label": _("Assets"), "fieldname": "asset_account", "fieldtype": "Data", "width": 300},
#         {"label": _("Amount"), "fieldname": "asset_amount", "fieldtype": "Currency", "options": currency, "width": 150},
#         {"label": _("Liabilities & Equity / Profit & Loss"), "fieldname": "liab_account", "fieldtype": "Data", "width": 300},
#         {"label": _("Amount"), "fieldname": "liab_amount", "fieldtype": "Currency", "options": currency, "width": 150},
#     ]

#     data = []

#     # --- Balance Sheet Roots ---
#     data.append({
#         "asset_account": _("Balance Sheet (Assets)"),
#         "account": "Balance Sheet Assets Root",
#         "parent_account": None,
#         "indent": 0,
#         "is_group": 1,
#         "show": 1
#     })

#     data.append({
#         "liab_account": _("Balance Sheet (Liabilities & Equity)"),
#         "account": "Balance Sheet Liabilities Root",
#         "parent_account": None,
#         "indent": 0,
#         "is_group": 1,
#         "show": 1
#     })

#     # Assets hierarchy
#     for row in assets:
#         data.append({
#             "asset_account": row.get("account_name"),
#             "asset_amount": row.get("total"),
#             "account": row.get("account"),
#             "parent_account": row.get("parent_account") or "Balance Sheet Assets Root",
#             "indent": row.get("indent", 1),
#             "is_group": row.get("is_group", 0)
#         })

#     # Liabilities & Equity hierarchy
#     for row in liab_equity:
#         data.append({
#             "liab_account": row.get("account_name"),
#             "liab_amount": row.get("total"),
#             "account": row.get("account"),
#             "parent_account": row.get("parent_account") or "Balance Sheet Liabilities Root",
#             "indent": row.get("indent", 1),
#             "is_group": row.get("is_group", 0)
#         })

#     # Profit & Loss under Expenses
#     data.append({
#         "liab_account": net_profit_loss.get("account_name"),
#         "liab_amount": net_profit_loss.get("total"),
#         "account": net_profit_loss.get("account"),
#         "parent_account": "PL Expense Root",
#         "indent": 0,
#         "is_group": 0
#     })

#     # --- Totals row at the bottom ---
#     data.append({
#         "asset_account": _("Total Assets (Top-Level)"),
#         "asset_amount": total_assets,
#         "liab_account": _("Total Liabilities & Equity (Top-Level)"),
#         "liab_amount": total_liab_equity + net_profit_loss.get("total"),
#         "indent": 0,
#         "is_group": 0
#     })

#     return columns, data






# import frappe
# from frappe import _
# from frappe.utils import cint, flt
# from erpnext.accounts.report.financial_statements import get_data, get_period_list


# def execute(filters=None):
# 	if not filters.get("period_start_date") or not filters.get("period_end_date"):
# 		frappe.throw(_("From Date and To Date are mandatory."))

# 	period_list = get_period_list(
# 		filters.from_fiscal_year,
# 		filters.to_fiscal_year,
# 		filters.period_start_date,
# 		filters.period_end_date,
# 		filters.filter_based_on,
# 		filters.periodicity,
# 		company=filters.company,
# 	)

# 	currency = filters.presentation_currency or frappe.get_cached_value(
# 		"Company", filters.company, "default_currency"
# 	)

# 	# --- Collect tree data ---
# 	assets = get_data(filters.company, "Asset", "Debit", period_list, filters=filters, accumulated_values=filters.accumulated_values)
# 	liabilities = get_data(filters.company, "Liability", "Credit", period_list, filters=filters, accumulated_values=filters.accumulated_values)
# 	equity = get_data(filters.company, "Equity", "Credit", period_list, filters=filters, accumulated_values=filters.accumulated_values)

# 	liab_equity = (liabilities or []) + (equity or [])

# 	# --- Columns ---
# 	columns = [
# 		{"label": _("Assets"), "fieldname": "asset_account", "fieldtype": "Data", "width": 300},
# 		{"label": _("Amount"), "fieldname": "asset_amount", "fieldtype": "Currency", "options": currency, "width": 150},
# 		{"label": _("Liabilities & Equity"), "fieldname": "liab_account", "fieldtype": "Data", "width": 300},
# 		{"label": _("Amount"), "fieldname": "liab_amount", "fieldtype": "Currency", "options": currency, "width": 150},
# 	]

# 	# --- Add section headings manually ---
# 	assets.insert(0, {"account_name": _("Application of Funds (Assets)"), "indent": 0, "total": None})
# 	liab_equity.insert(0, {"account_name": _("Source of Funds (Liabilities & Equity)"), "indent": 0, "total": None})

# 	# --- Balance both sides ---
# 	max_len = max(len(assets), len(liab_equity))
# 	data = []
# 	for i in range(max_len):
# 		asset_row = assets[i] if i < len(assets) else {}
# 		liab_row = liab_equity[i] if i < len(liab_equity) else {}

# 		data.append({
# 			"asset_account": asset_row.get("account_name"),
# 			"asset_amount": asset_row.get("total"),
# 			"liab_account": liab_row.get("account_name"),
# 			"liab_amount": liab_row.get("total"),
# 			"indent": asset_row.get("indent", 0)  # indent mainly for assets side
# 		})

# 	# --- Totals ---
# 	total_assets = sum([a.get("total", 0) for a in assets if a.get("total")])
# 	total_liab = sum([l.get("total", 0) for l in liab_equity if l.get("total")])

# 	# data.append({
# 	# 	"asset_account": _("Total Assets"),
# 	# 	"asset_amount": total_assets,
# 	# 	"liab_account": _("Total Liabilities & Equity"),
# 	# 	"liab_amount": total_liab,
# 	# 	"indent": 0
# 	# })

# 	return columns, data

