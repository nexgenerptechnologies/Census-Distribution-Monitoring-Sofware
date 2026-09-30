frappe.ui.form.on("Census Stock", {
    refresh: function(frm) {
        frm.disable_save();
        frm.page.set_primary_action(__("Refresh Stock"), function() {
            frm.reload_doc();
        }, "refresh");

        frm.add_custom_button(__("Export Stock to CSV / Excel"), function() {
            window.open("/api/method/census_distribution_monitoring_software.census_distribution_monitoring_software.api.download_stock_csv", "_blank");
        }, __("Export"));
    }
});
