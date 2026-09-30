import frappe
from frappe import _
from frappe.model.document import Document

class CensusStockEntry(Document):
    def validate(self):
        if not self.items:
            frappe.throw(_("Please add at least one item to this Stock Entry."))
        for row in self.items:
            if not row.quantity or row.quantity <= 0:
                frappe.throw(_("Quantity for item {0} must be greater than zero.").format(row.item_name or row.item))
