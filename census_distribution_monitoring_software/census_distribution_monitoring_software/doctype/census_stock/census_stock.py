import frappe
from frappe.model.document import Document
from census_distribution_monitoring_software.census_distribution_monitoring_software.api import get_stock_balance

class CensusStock(Document):
    def load_from_db(self):
        super().load_from_db()
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
                "total_inward": it.get("total_inward"),
                "total_dispatched": it.get("total_dispatched"),
                "available_balance": it.get("balance"),
            })

@frappe.whitelist()
def get_live_stock_data():
    return get_stock_balance()
