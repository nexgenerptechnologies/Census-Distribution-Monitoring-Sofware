frappe.ui.form.on("Census Dispatch", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Print All Box Labels"), function() {
                var url = "/printview?doctype=Census%20Dispatch&name=" + encodeURIComponent(frm.doc.name) + "&format=Speed%20Post%20Dispatch%20Label";
                window.open(url, "_blank");
            }, __("Print"));
        }
    },

    state: function(frm) {
        if (frm.doc.state) {
            frappe.db.get_doc("Census State", frm.doc.state).then(function(state_doc) {
                frm.set_value("consignee_name", state_doc.consignee_name || "DIRECTOR OF CENSUS OPERATIONS");
                frm.set_value("delivery_address", state_doc.delivery_address || "");
                frm.set_value("pincode", state_doc.pincode || "");
                frm.set_value("state_code", state_doc.state_code || "");
            });
        }
    }
});

frappe.ui.form.on("Census Dispatch Box", {
    boxes_add: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        // Fetch next speed post number from settings
        frappe.call({
            method: "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_settings.census_settings.get_next_speed_post_number",
            callback: function(r) {
                if (r && r.message) {
                    frappe.model.set_value(cdt, cdn, "speed_post_serial", r.message.serial_number);
                    frappe.model.set_value(cdt, cdn, "speed_post_barcode", r.message.article_no);
                }
            }
        });
        
        // Auto set box index
        var total = frm.doc.boxes.length;
        frappe.model.set_value(cdt, cdn, "box_no", total + " of " + total);
        frm.trigger("recompute_box_numbers");
    },

    recompute_box_numbers: function(frm) {
        var count = frm.doc.boxes.length;
        frm.doc.boxes.forEach(function(row, idx) {
            row.box_no = (idx + 1) + " of " + count;
        });
        frm.refresh_field("boxes");
    }
});
