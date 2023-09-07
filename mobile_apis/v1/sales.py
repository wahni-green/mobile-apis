# Copyright (c) 2022, Wahni IT Solutions and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import today, add_days
from erpnext.stock.get_item_details import get_price_list_rate_for


# GET ORDERS DETAIL VIEW
@frappe.whitelist(allowed_methods=["GET"])
def get_order_details():
	try:
		data = json.loads(frappe.request.data)
		doc = frappe.db.get_value('Sales Order', data.get("order_id"), [
			'transaction_date', 'delivery_date', 'customer', 'status'
		], as_dict=1)

		if doc:
			doc['items'] = frappe.get_all("Sales Order Item", filters={
				'parent': data.get("order_id"),
				"is_free_item": 0
			}, fields=['item_code', 'item_name', 'qty', 'rate', 'amount'])

		return {"success": True, "order_details": doc}
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()),  "Order Details error")
		return {"success": False, "message": str(e)}


# SALES ORDER CREATION
@frappe.whitelist(allowed_methods=["POST"])
def create_sales_order():
	try:
		frappe.db.commit()
		data = json.loads(frappe.request.data)
		items = data.get("items")

		sales_order = frappe.new_doc("Sales Order")
		sales_order.customer = data.get("distributor")
		sales_order.delivery_date = add_days(today(), 20)
		if data.get("company"):
			sales_order.company = data.get("company")

		sales_order.selling_price_list = frappe.db.get_value(
			"Customer", sales_order.customer, "default_price_list"
		) or "Distributor"

		for item in items:
			rate = get_price_list_rate_for(
				{
					"price_list": sales_order.selling_price_list,
					"uom": frappe.db.get_value("Item", item.get("item_code"), "sales_uom") or "Box",
					"transaction_date": today(),
					"qty": 1
				},
				item.get("item_code"),
			) or 0

			sales_order.append('items', {
				"item_code": item.get("item_code"),
				"qty": item.get("qty"),
				"rate": rate,
			})

		if not data.get("sales_person"):
			data["sales_person"] = frappe.get_value(
				"Sales Person",
				filters={
					"employee": frappe.get_value(
						"Employee",
						filters={"user_id": frappe.session.user}
					)
				}
			)

		if data.get("sales_person"):
			sp = sales_order.append('sales_team', {})
			sp.sales_person = data.get("sales_person")
			sp.allocated_percentage = 100

		sales_order.flags.ignore_permissions = True
		sales_order.set_missing_values()
		sales_order.calculate_taxes_and_totals()

		sales_order.insert(ignore_permissions=True, ignore_mandatory=True)
		sales_order.submit()

		return {"success": True, "message": "Sales Order Created"}
	except Exception as e:
		frappe.log_error(str(frappe.get_traceback()), "Sales Order Error")
		frappe.db.rollback()
		return {"success": False, "message": str(e)}

