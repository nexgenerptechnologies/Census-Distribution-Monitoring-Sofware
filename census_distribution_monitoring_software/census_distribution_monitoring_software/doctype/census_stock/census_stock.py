import frappe
from frappe.model.document import Document
from census_distribution_monitoring_software.census_distribution_monitoring_software.api import get_stock_balance

class CensusStock(Document):
    def before_save(self):
        self.populate_live_stock()

    def populate_live_stock(self):
        stock_data = get_stock_balance()
        kit = stock_data.get("kit_stock", {})
        self.kit_item_name = kit.get("item_name", "Enumerator Kit Set")
        self.kit_available_stock = kit.get("balance", 0.0)
        self.kit_total_inward = kit.get("total_inward", 0.0)
        self.kit_total_dispatched = kit.get("total_dispatched", 0.0)

        self.loose_items = []
        for it in stock_data.get("loose_items", []):
            self.append("loose_items", {
                "sr_no": it.get("sr_no"),
                "item_code": it.get("item_code"),
                "item_name": it.get("item_name"),
                "uom": it.get("uom"),
                "total_inward": it.get("total_inward", 0.0),
                "total_dispatched": it.get("total_dispatched", 0.0),
                "available_balance": it.get("balance", 0.0),
            })

@frappe.whitelist()
def refresh_and_get_stock():
    doc = frappe.get_single("Census Stock")
    doc.populate_live_stock()
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return doc
