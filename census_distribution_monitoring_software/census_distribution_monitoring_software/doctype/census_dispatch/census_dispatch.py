import frappe
from frappe import _
from frappe.model.document import Document

class CensusDispatch(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_boxes()

    def calculate_totals(self):
        if self.boxes:
            self.total_boxes = len(self.boxes)
            self.total_weight_kg = sum(flt(b.weight_kg) for b in self.boxes)
            kits_in_boxes = sum(flt(b.kits_count) for b in self.boxes)
            if kits_in_boxes > 0 and (not self.total_kits or self.total_kits == 0):
                self.total_kits = kits_in_boxes

    def validate_boxes(self):
        if not self.boxes:
            frappe.throw(_("Please add at least one Box in the Dispatch Consignment."))

        seen_unique_boxes = set()
        for idx, box in enumerate(self.boxes, 1):
            if not box.unique_box_no:
                frappe.throw(_("Row #{0}: Unique Box No. is required.").format(idx))
            if box.unique_box_no in seen_unique_boxes:
                frappe.throw(_("Row #{0}: Duplicate Unique Box No. {1} found in this dispatch.").format(idx, box.unique_box_no))
            seen_unique_boxes.add(box.unique_box_no)

            if not box.speed_post_barcode:
                frappe.throw(_("Row #{0}: Speed Post Barcode / Article No. is required.").format(idx))

    def on_submit(self):
        self.status = "Dispatched"
        # Validate stock availability
        from census_distribution_monitoring_software.census_distribution_monitoring_software.api import get_stock_balance
        stock = get_stock_balance()
        
        # Check kit stock if kits are dispatched
        if self.total_kits and self.total_kits > 0:
            kit_stock = stock.get("kit_stock", {}).get("balance", 0)
            if kit_stock < self.total_kits:
                frappe.msgprint(
                    _("Warning: Dispatched {0} Kits, but current available Kit Stock is {1}.").format(
                        self.total_kits, kit_stock
                    ),
                    indicator="orange",
                    alert=True
                )

def flt(val):
    try:
        return float(val or 0.0)
    except (ValueError, TypeError):
        return 0.0
