import frappe
from frappe.model.document import Document

class CensusSettings(Document):
    pass

@frappe.whitelist()
def get_next_speed_post_number():
    settings = frappe.get_single("Census Settings")
    current = settings.speed_post_current_number or settings.speed_post_start_series or 40000
    prefix = settings.speed_post_prefix or "EN"
    suffix = settings.speed_post_suffix or "IN"
    padding = settings.speed_post_number_padding or 9
    
    # India Post Speed Post Article Number format: e.g. EN + 9 digits + IN
    # If number is 40001, formatted as EN000040001IN or user-defined padding
    formatted_num = str(current).zfill(padding)
    article_no = f"{prefix}{formatted_num}{suffix}"
    
    # Auto-increment for next
    settings.speed_post_current_number = current + 1
    settings.save(ignore_permissions=True)
    
    return {
        "serial_number": current,
        "article_no": article_no
    }
