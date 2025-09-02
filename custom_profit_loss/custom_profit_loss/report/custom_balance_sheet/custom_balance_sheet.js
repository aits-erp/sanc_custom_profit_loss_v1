frappe.query_reports["Custom Balance Sheet"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Custom Balance Sheet", 10);

// Filters
frappe.query_reports["Custom Balance Sheet"]["filters"].push({
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

frappe.query_reports["Custom Balance Sheet"]["filters"].push({
	fieldname: "accumulated_values",
	label: __("Accumulated Values"),
	fieldtype: "Check",
	default: 1,
});

frappe.query_reports["Custom Balance Sheet"]["filters"].push({
	fieldname: "include_default_book_entries",
	label: __("Include Default FB Entries"),
	fieldtype: "Check",
	default: 1,
});

// ✅ Force tree only on one column (asset_account)
frappe.query_reports["Custom Balance Sheet"].get_datatable_options = function(options) {
	return Object.assign(options, {
		treeView: true,
		columns: options.columns.map(col => {
			if (col.fieldname === "asset_account") {
				col.is_tree = true;   // 👈 only assets control expand/collapse
			}
			if (col.fieldname === "liab_account") {
				// just display text, no tree toggle
				col.is_tree = false;
			}
			return col;
		})
	});
};





// // Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// // License: GNU General Public License v3. See license.txt

// frappe.query_reports["Custom Balance Sheet"] = $.extend({}, erpnext.financial_statements);

// erpnext.utils.add_dimensions("Custom Balance Sheet", 10);

// frappe.query_reports["Custom Balance Sheet"]["filters"].push({
// 	fieldname: "selected_view",
// 	label: __("Select View"),
// 	fieldtype: "Select",
// 	options: [
// 		{ value: "Report", label: __("Report View") },
// 		{ value: "Growth", label: __("Growth View") },
// 	],
// 	default: "Report",
// 	reqd: 1,
// });

// frappe.query_reports["Custom Balance Sheet"]["filters"].push({
// 	fieldname: "accumulated_values",
// 	label: __("Accumulated Values"),
// 	fieldtype: "Check",
// 	default: 1,
// });

// frappe.query_reports["Custom Balance Sheet"]["filters"].push({
// 	fieldname: "include_default_book_entries",
// 	label: __("Include Default FB Entries"),
// 	fieldtype: "Check",
// 	default: 1,
// });


