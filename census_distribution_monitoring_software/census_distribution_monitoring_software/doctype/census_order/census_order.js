frappe.ui.form.on("Census Order", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Sync Dispatches"), function() {
                frappe.call({
                    method: "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_order.census_order.sync_order_dispatches",
                    args: { order_name: frm.doc.name },
                    callback: function(r) {
                        frappe.msgprint(__("Order dispatches synced successfully!"));
                        frm.reload_doc();
                    }
                });
            }, __("Actions"));
        }
    },

    ordered_kits: function(frm) {
        var ordered = flt(frm.doc.ordered_kits);
        var dispatched = flt(frm.doc.dispatched_kits);
        frm.set_value("pending_kits", Math.max(0, ordered - dispatched));
        if (ordered > 0) {
            frm.set_value("completion_percent", Math.min(100, Math.round((dispatched / ordered) * 100)));
        }
    }
});
