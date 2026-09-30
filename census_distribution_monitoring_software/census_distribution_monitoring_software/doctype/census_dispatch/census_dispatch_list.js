frappe.listview_settings['Census Dispatch'] = {
    onload: function(listview) {
        // 1. Add State dropdown selector to filter list by state
        frappe.call({
            method: "census_distribution_monitoring_software.census_distribution_monitoring_software.api.get_states",
            callback: function(r) {
                if (r && r.message) {
                    var options = ['<option value="">-- All States & UTs --</option>'];
                    r.message.forEach(function(st) {
                        options.push('<option value="' + st.name + '">' + (st.display_name || st.name) + '</option>');
                    });

                    var state_select = $(
                        '<div class="form-group" style="margin: 0 10px 0 0; display: inline-block;">' +
                        '<select class="form-control form-control-sm" id="census-state-filter" style="min-width: 220px; font-weight: 600;">' +
                        options.join('') +
                        '</select>' +
                        '</div>'
                    );

                    listview.page.add_field({
                        fieldtype: 'Link',
                        fieldname: 'filter_state',
                        options: 'Census State',
                        label: __('Filter by State'),
                        change: function() {
                            var val = this.get_value();
                            listview.filter_area.remove('state');
                            if (val) {
                                listview.filter_area.add([['Census Dispatch', 'state', '=', val]]);
                            }
                            listview.refresh();
                        }
                    });
                }
            }
        });

        // 2. Add Export to Excel / CSV button for Department Officials
        listview.page.add_inner_button(__('Download Dispatches (Excel/CSV)'), function() {
            window.open('/api/method/census_distribution_monitoring_software.census_distribution_monitoring_software.api.download_dispatches_csv', '_blank');
        }, __('Export'));

        // 3. Add Export Stock Summary button
        listview.page.add_inner_button(__('Download Stock Report'), function() {
            window.open('/api/method/census_distribution_monitoring_software.census_distribution_monitoring_software.api.download_stock_csv', '_blank');
        }, __('Export'));
    }
};
