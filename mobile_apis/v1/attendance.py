# Copyright (c) 2022, Wahni IT Solutions and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import today


# FETCH ATTENDANCE
@frappe.whitelist(allowed_methods=["GET"])
def get_attendance_status(employee=None, date=None):
	try:
		if not employee:
			employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, 'name')

		if not employee:
			return {"status": True, "attendance": None, "late_entry": 0}
		
		if not date:
			date = today()

		attendance = frappe.get_value("Attendance", {
			"employee": employee,
			"docstatus": 1,
			"attendance_date": date
		}, ["status", "late_entry"], as_dict=1)

		if not attendance:
			return {"status": True, "attendance": None, "late_entry": 0}
		
		return {"status": True, "attendance": attendance.status, "late_entry": attendance.late_entry}
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()), "Attendance status error")
		return {"success": False, "error": str(e)}


# MARK ATTENDANCE
@frappe.whitelist(allowed_methods=["POST"])
def mark_attendance():
	try:
		employee = json.loads(frappe.request.data).get("employee")
		if not employee:
			employee = frappe.get_value("Employee", {"user_id": frappe.session.user})
		
		if not employee:
			return {"success": False, "message": "Employee not found."}

		if frappe.get_value("Attendance", {
			"employee": employee,
			"docstatus": 1,
			"attendance_date": today()
		}):
			return {"success": False, "message": "Attendance already marked."}

		att = frappe.new_doc("Attendance")
		att.employee = employee
		att.attendance_date = today()
		att.insert(ignore_permissions=True, ignore_mandatory=True)
		att.submit()
		return {"success": True, "message": "Attendance Marked."}
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()), "Mark Attendance error")
		return {"success": False, "message": "Could not mark attendance"}
