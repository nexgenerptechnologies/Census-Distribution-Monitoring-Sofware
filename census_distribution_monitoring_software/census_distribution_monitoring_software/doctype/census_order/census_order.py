import frappe
from frappe.model.document import Document

class CensusOrder(Document):
    def validate(self):
        self.calculate_dispatches()

    def calculate_dispatches(self):
        dispatched = sum(float(d.kits_count or 0) for d in (self.dispatches or []))
        self.dispatched_kits = dispatched
        ordered = float(self.ordered_kits or 0)
        self.pending_kits = max(0.0, ordered - dispatched)
        
        if ordered > 0:
            self.completion_percent = min(100.0, round((dispatched / ordered) * 100.0, 2))
        else:
            self.completion_percent = 0.0

        if dispatched == 0:
            self.status = "Pending"
        elif dispatched >= ordered:
            self.status = "Completed"
        else:
            self.status = "Partially Dispatched"

@frappe.whitelist()
def sync_order_dispatches(order_name):
    """Sync all dispatches made for this order"""
    order = frappe.get_doc("Census Order", order_name)
    # Fetch dispatches linked to this order or state
    dispatches = frappe.get_all(
        "Census Dispatch",
        filters={"order": order_name, "docstatus": 1},
        fields=["name", "dispatch_date", "total_kits", "total_boxes", "status"],
        order_by="dispatch_date asc"
    )

    order.dispatches = []
    for d in dispatches:
        order.append("dispatches", {
            "dispatch_id": d.name,
            "dispatch_date": d.dispatch_date,
            "kits_count": d.total_kits,
            "boxes_count": d.total_boxes,
            "status": d.status
        })

    order.save(ignore_permissions=True)
    return order
