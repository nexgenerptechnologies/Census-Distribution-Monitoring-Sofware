frappe.ui.form.on("Census Stock", {
    refresh: function(frm) {
        frm.disable_save();
        frm.page.set_primary_action(__("Refresh Stock"), function() {
            frappe.call({
                method: "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_stock.census_stock.refresh_and_get_stock",
                freeze: true,
                freeze_message: __("Calculating real-time stock balances..."),
                callback: function(r) {
                    frm.reload_doc();
                }
            });
        }, "refresh");

        frm.add_custom_button(__("Export Stock to CSV / Excel"), function() {
            window.open("/api/method/census_distribution_monitoring_software.census_distribution_monitoring_software.api.download_stock_csv", "_blank");
        }, __("Export"));
    },
    onload: function(frm) {
        frappe.call({
            method: "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_stock.census_stock.refresh_and_get_stock",
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                }
            }
        });
    }
});
