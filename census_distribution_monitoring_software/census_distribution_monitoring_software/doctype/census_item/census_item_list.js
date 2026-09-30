frappe.listview_settings['Census Item'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Load Default Census Items'), function() {
            frappe.call({
                method: 'census_distribution_monitoring_software.setup_data.reload_defaults',
                freeze: true,
                freeze_message: __('Loading default Census items and states...'),
                callback: function(r) {
                    frappe.msgprint(r.message.message || __('Defaults loaded!'));
                    listview.refresh();
                }
            });
        });
    }
};
