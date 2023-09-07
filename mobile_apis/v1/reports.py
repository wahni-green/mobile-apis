# Copyright (c) 2022, Wahni IT Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.query_report import build_xlsx_data
from frappe.utils import now, today, global_date_format, format_time
from frappe.utils.csvutils import to_csv
from frappe.utils.pdf import get_pdf
from frappe.utils.xlsxutils import make_xlsx


def get_report_content(filters, report, format="CSV"):
	"""Returns file in for the report in given format"""
	report = frappe.get_doc("Report", report)
	filters = frappe.parse_json(filters) if filters else {}

	columns, data = report.get_data(
		limit=100,
		user=frappe.session.user,
		filters=filters,
		as_dict=True,
		ignore_prepared_report=True,
	)

	# add serial numbers
	columns.insert(0, frappe._dict(fieldname="idx", label="", width="30px"))
	for i in range(len(data)):
		data[i]["idx"] = i + 1

	if len(data) == 0:
		frappe.throw(_("No data found."))

	if format == "PDF":
		columns = update_field_types(columns)
		html = get_html_table(report.name, filters, columns, data)
		return get_pdf(html, {"orientation": "Landscape", "page-size": "A3"})

	elif format == "XLSX":
		report_data = frappe._dict()
		report_data["columns"] = columns
		report_data["result"] = data

		xlsx_data, column_widths = build_xlsx_data(columns, report_data, [], 1, ignore_visible_idx=True)
		xlsx_file = make_xlsx(xlsx_data, "Report", column_widths=column_widths)
		return xlsx_file.getvalue()

	elif format == "CSV":
		report_data = frappe._dict()
		report_data["columns"] = columns
		report_data["result"] = data

		xlsx_data, column_widths = build_xlsx_data(columns, report_data, [], 1, ignore_visible_idx=True)
		return to_csv(xlsx_data)

	else:
		frappe.throw(_("Invalid Output Format"))


def update_field_types(columns):
	for col in columns:
		if col.fieldtype in ("Link", "Dynamic Link", "Currency") and col.options != "Currency":
			col.fieldtype = "Data"
			col.options = ""
	return columns


def get_html_table(report, filters=None, columns=None, data=None):
    date_time = global_date_format(now()) + " " + format_time(now())
    # create new HTML template if required
    return frappe.render_template(
        "frappe/templates/emails/auto_email_report.html",
        {
            "title": report,
            "description": report,
            "date_time": date_time,
            "columns": columns,
            "data": data,
            "report_url": "",
            "report_name": report,
            "edit_report_settings": "",
        },
    )


@frappe.whitelist()
def download_report(filters, report, format="PDF"):
	try:
		frappe.local.response.filecontent = get_report_content(filters, report, format)
		frappe.local.response.type = "download"
		frappe.local.response.filename = f"{report}-{today()}.{format.lower()}"
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()), f"Error downloading {report} report")
		frappe.throw(str(e))
		# return {"success": False, "error": str(e)}
