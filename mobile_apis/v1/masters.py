# Copyright (c) 2022, Wahni IT Solutions and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _


@frappe.whitelist(allowed_methods=["GET"])
def fetch_customers():
	try:
		return {"success": True, "customers": frappe.get_list('Customer', fields=['name', 'customer_name', 'customer_group', 'territory'])}
	except Exception as e:
		return {"success": False, "message": str(e)}


@frappe.whitelist(allowed_methods=["POST"])
def create_customer():
	try:
		data = json.loads(frappe.request.data)
		customer = frappe.new_doc("Customer")

		for key, value in data.items():
			customer.set(key, value)

		customer.insert(ignore_permissions=True, ignore_mandatory=True)
		return {"success": True, "message": "Customer Created"}
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()), "Customer Creation Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allowed_methods=["GET"])
def fetch_customer_groups():
	try:
		return {"success": True, "customer_groups": frappe.get_list('Customer Group')}
	except Exception as e:
		return {"success": False, "message": str(e)}


@frappe.whitelist(allowed_methods=["GET"])
def fetch_item_groups():
	try:
		return {"success": True, "item_groups": frappe.get_list('Item Group')}
	except Exception as e:
		return {"success": False, "message": str(e)}


@frappe.whitelist(allowed_methods=["GET"])
def fetch_items():
	try:
		return {"success": True, "items": frappe.get_list('Item', fields=['name', 'item_name', 'item_group', 'stock_uom', 'sales_uom'])}
	except Exception as e:
		return {"success": False, "message": str(e)}