import frappe
from census_distribution_monitoring_software.census_distribution_monitoring_software.api import (
    get_stock_balance, get_states, get_order_vs_dispatch_summary
)

def get_context(context):
    context.no_cache = 1
    
    # Require login for customer portal
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/tracking"
        raise frappe.Redirect
    
    context.user_full_name = frappe.utils.get_fullname(frappe.session.user)
    context.settings = frappe.get_single("Census Settings")
    context.states = get_states()
    context.stock_data = get_stock_balance()
    context.summary_data = get_order_vs_dispatch_summary()
    context.title = "Census Distribution Monitoring Software"
    
    return context
