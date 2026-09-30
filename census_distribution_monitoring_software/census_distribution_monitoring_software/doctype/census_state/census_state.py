import frappe
from frappe.model.document import Document

class CensusState(Document):
    def before_save(self):
        if self.state_name and self.state_code:
            self.display_name = f"{self.state_name} ({self.state_code})"
        elif self.state_name:
            self.display_name = self.state_name
