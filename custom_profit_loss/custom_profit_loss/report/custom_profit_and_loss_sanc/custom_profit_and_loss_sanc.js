// Copyright (c) 2025, pankaj and contributors
// For license information, please see license.txt

// frappe.query_reports["Custom Profit and Loss Sanc"] = {
// 	"filters": [

// 	]
// };



frappe.query_reports["Custom Profit and Loss Sanc"] = {
    "filters": []
};

frappe.query_reports["Custom Profit and Loss Sanc"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Custom Profit and Loss Sanc", 10);

// Filters
frappe.query_reports["Custom Profit and Loss Sanc"]["filters"].push({
    fieldname: "selected_view",
    label: __("Select View"),
    fieldtype: "Select",
    options: [
        { value: "Report", label: __("Report View") },
        { value: "Growth", label: __("Growth View") },
    ],
    default: "Report",
    reqd: 1,
});

frappe.query_reports["Custom Profit and Loss Sanc"]["filters"].push({
    fieldname: "accumulated_values",
    label: __("Accumulated Values"),
    fieldtype: "Check",
    default: 1,
});

frappe.query_reports["Custom Profit and Loss Sanc"]["filters"].push({
    fieldname: "include_default_book_entries",
    label: __("Include Default FB Entries"),
    fieldtype: "Check",
    default: 1,
});

// ✅ Force tree only on one column (asset_account) and bold Net Profit / Loss
frappe.query_reports["Custom Profit and Loss Sanc"].get_datatable_options = function(options) {
    return Object.assign(options, {
        treeView: true,
        columns: options.columns.map(col => {
            if (col.fieldname === "asset_account") {
                col.is_tree = true;   // only assets control expand/collapse
            }

        if (col.fieldname === "expense_account") {
    col.formatter = function(value, row, colDef, dataContext) {
        if (dataContext && dataContext.account === "Net P&L") {
            // Wrap in span with class and style
            return `<span style="font-weight: bold;">${value}</span>`;
        }
        return value || "";
    };
}



            return col;
        })
    });
};
