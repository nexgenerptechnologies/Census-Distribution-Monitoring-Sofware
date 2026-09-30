import frappe

def after_install():
    load_default_data()

def after_migrate():
    load_default_data()

@frappe.whitelist()
def reload_defaults():
    """Whitelisted function that can be called anytime to ensure default items, kit bundle, and states exist."""
    return load_default_data()

def load_default_data():
    items_created = create_items()
    states_created = create_states()
    settings_configured = configure_settings()
    configure_permissions()
    frappe.db.commit()
    return {
        "status": "success",
        "message": f"Successfully loaded {items_created} Items (including Enumerator Kit Bundle with 10 constituent items), {states_created} States, and configured Settings."
    }

def create_items():
    # 1. The 10 Loose Items
    loose_items = [
        {
            "item_code": "LOOSE-01-BAG",
            "item_name": "Water Resistant Carry Bag with Census Logo",
            "sr_no": 1,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Water Resistant Carry Bag with Census Logo (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-02-BOARD",
            "item_name": "Foldable Writing Board with 2 detachable binder clips",
            "sr_no": 2,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Foldable Writing Board with 2 detachable binder clips (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-03-NOTEPAD",
            "item_name": "Spiral Notepad",
            "sr_no": 3,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Spiral Notepad (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-04-CAP",
            "item_name": "White Cap with Census Logo",
            "sr_no": 4,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "White Cap with Census Logo (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-05-LANYARD",
            "item_name": "Lanyard for Identity Card with transparent pouch",
            "sr_no": 5,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Lanyard for Identity Card with transparent pouch (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-06-MARKER",
            "item_name": "Marker Pens (Red-1 and Black-1)",
            "sr_no": 6,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Marker Pens (Red-1 and Black-1) (Qty 2 per Kit)"
        },
        {
            "item_code": "LOOSE-07-PEN",
            "item_name": "Ball Point Pen (Blue-1 and Black-1)",
            "sr_no": 7,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Ball Point Pen (Blue-1 and Black-1) (Qty 2 per Kit)"
        },
        {
            "item_code": "LOOSE-08-PENCIL",
            "item_name": "Pencil",
            "sr_no": 8,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Pencil (Qty 2 per Kit)"
        },
        {
            "item_code": "LOOSE-09-SHARPENER",
            "item_name": "Sharpener",
            "sr_no": 9,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Sharpener (Qty 1 per Kit)"
        },
        {
            "item_code": "LOOSE-10-ERASER",
            "item_name": "Eraser",
            "sr_no": 10,
            "is_kit_set": 0,
            "uom": "Nos",
            "is_active": 1,
            "description": "Eraser (Qty 1 per Kit)"
        }
    ]

    count = 0
    for it in loose_items:
        if not frappe.db.exists("Census Item", it["item_code"]):
            doc = frappe.new_doc("Census Item")
            doc.update(it)
            doc.insert(ignore_permissions=True)
            count += 1
        else:
            doc = frappe.get_doc("Census Item", it["item_code"])
            doc.update(it)
            doc.save(ignore_permissions=True)

    # 2. Finished Goods: Enumerator Kit Set with Kit Bundle child table
    kit_bundle_items = [
        {"item": "LOOSE-01-BAG", "item_name": "Water Resistant Carry Bag with Census Logo", "sr_no": 1, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-02-BOARD", "item_name": "Foldable Writing Board with 2 detachable binder clips", "sr_no": 2, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-03-NOTEPAD", "item_name": "Spiral Notepad", "sr_no": 3, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-04-CAP", "item_name": "White Cap with Census Logo", "sr_no": 4, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-05-LANYARD", "item_name": "Lanyard for Identity Card with transparent pouch", "sr_no": 5, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-06-MARKER", "item_name": "Marker Pens (Red-1 and Black-1)", "sr_no": 6, "quantity": 2, "uom": "Nos"},
        {"item": "LOOSE-07-PEN", "item_name": "Ball Point Pen (Blue-1 and Black-1)", "sr_no": 7, "quantity": 2, "uom": "Nos"},
        {"item": "LOOSE-08-PENCIL", "item_name": "Pencil", "sr_no": 8, "quantity": 2, "uom": "Nos"},
        {"item": "LOOSE-09-SHARPENER", "item_name": "Sharpener", "sr_no": 9, "quantity": 1, "uom": "Nos"},
        {"item": "LOOSE-10-ERASER", "item_name": "Eraser", "sr_no": 10, "quantity": 1, "uom": "Nos"},
    ]

    kit_code = "KIT-ENUMERATOR-01"
    if not frappe.db.exists("Census Item", kit_code):
        kit_doc = frappe.new_doc("Census Item")
        kit_doc.item_code = kit_code
        kit_doc.item_name = "Enumerator Kit Set"
        kit_doc.sr_no = 0
        kit_doc.is_kit_set = 1
        kit_doc.uom = "Set"
        kit_doc.is_active = 1
        kit_doc.description = "Complete Enumerator Kit Set containing items Sr. No. 1 to 10 as per official Annexure-I"
        
        for k_item in kit_bundle_items:
            kit_doc.append("kit_items", k_item)
            
        kit_doc.insert(ignore_permissions=True)
        count += 1
    else:
        kit_doc = frappe.get_doc("Census Item", kit_code)
        kit_doc.is_kit_set = 1
        kit_doc.uom = "Set"
        kit_doc.kit_items = []
        for k_item in kit_bundle_items:
            kit_doc.append("kit_items", k_item)
        kit_doc.save(ignore_permissions=True)

    return count

def create_states():
    states = [
        {"state_code": "01", "state_name": "Jammu & Kashmir", "display_name": "Jammu & Kashmir (01)"},
        {"state_code": "02", "state_name": "Himachal Pradesh", "display_name": "Himachal Pradesh (02)"},
        {"state_code": "03", "state_name": "Punjab", "display_name": "Punjab (03)"},
        {"state_code": "04", "state_name": "Chandigarh", "display_name": "Chandigarh (04)"},
        {"state_code": "05", "state_name": "Uttarakhand", "display_name": "Uttarakhand (05)"},
        {"state_code": "06", "state_name": "Haryana", "display_name": "Haryana (06)"},
        {"state_code": "07", "state_name": "NCT of Delhi", "display_name": "NCT of Delhi (07)"},
        {"state_code": "08", "state_name": "Rajasthan", "display_name": "Rajasthan (08)"},
        {"state_code": "09", "state_name": "Uttar Pradesh", "display_name": "Uttar Pradesh (09)"},
        {"state_code": "10", "state_name": "Bihar", "display_name": "Bihar (10)"},
        {"state_code": "11", "state_name": "Sikkim", "display_name": "Sikkim (11)"},
        {"state_code": "12", "state_name": "Arunachal Pradesh", "display_name": "Arunachal Pradesh (12)"},
        {"state_code": "13", "state_name": "Nagaland", "display_name": "Nagaland (13)"},
        {"state_code": "14", "state_name": "Manipur", "display_name": "Manipur (14)"},
        {"state_code": "15", "state_name": "Mizoram", "display_name": "Mizoram (15)"},
        {"state_code": "16", "state_name": "Tripura", "display_name": "Tripura (16)"},
        {"state_code": "17", "state_name": "Meghalaya", "display_name": "Meghalaya (17)"},
        {
            "state_code": "18", 
            "state_name": "Assam", 
            "display_name": "Assam (18)", 
            "consignee_name": "DIRECTOR OF CENSUS OPERATIONS ASSAM",
            "delivery_address": "'Achyut Plaza', Behind Hub Complex,\nGUWAHATI-781005",
            "pincode": "781005"
        },
        {"state_code": "19", "state_name": "West Bengal", "display_name": "West Bengal (19)"},
        {"state_code": "20", "state_name": "Jharkhand", "display_name": "Jharkhand (20)"},
        {"state_code": "21", "state_name": "Odisha", "display_name": "Odisha (21)"},
        {"state_code": "22", "state_name": "Chhattisgarh", "display_name": "Chhattisgarh (22)"},
        {"state_code": "23", "state_name": "Madhya Pradesh", "display_name": "Madhya Pradesh (23)"},
        {"state_code": "24", "state_name": "Gujarat", "display_name": "Gujarat (24)"},
        {"state_code": "25", "state_name": "Daman & Diu", "display_name": "Daman & Diu (25)"},
        {"state_code": "26", "state_name": "Dadra & Nagar Haveli", "display_name": "Dadra & Nagar Haveli (26)"},
        {"state_code": "27", "state_name": "Maharashtra", "display_name": "Maharashtra (27)"},
        {"state_code": "28", "state_name": "Andhra Pradesh", "display_name": "Andhra Pradesh (28)"},
        {"state_code": "29", "state_name": "Karnataka", "display_name": "Karnataka (29)"},
        {"state_code": "30", "state_name": "Goa", "display_name": "Goa (30)"},
        {"state_code": "31", "state_name": "Lakshadweep", "display_name": "Lakshadweep (31)"},
        {"state_code": "32", "state_name": "Kerala", "display_name": "Kerala (32)"},
        {"state_code": "33", "state_name": "Tamil Nadu", "display_name": "Tamil Nadu (33)"},
        {"state_code": "34", "state_name": "Puducherry", "display_name": "Puducherry (34)"},
        {"state_code": "35", "state_name": "Andaman & Nicobar Islands", "display_name": "Andaman & Nicobar Islands (35)"},
        {"state_code": "36", "state_name": "Telangana", "display_name": "Telangana (36)"},
        {"state_code": "37", "state_name": "Ladakh", "display_name": "Ladakh (37)"},
    ]

    count = 0
    for st in states:
        doc_name = st["display_name"]
        if not frappe.db.exists("Census State", doc_name):
            doc = frappe.new_doc("Census State")
            doc.update(st)
            if not doc.consignee_name:
                doc.consignee_name = f"DIRECTOR OF CENSUS OPERATIONS {st['state_name'].upper()}"
            doc.insert(ignore_permissions=True)
            count += 1
    return count

def configure_settings():
    settings = frappe.get_single("Census Settings")
    settings.project_name = "CENSUS-2027 PROJECT"
    settings.booked_from = "Speed Post Center"
    settings.bnpl_code = "901-559"
    settings.customer_id = "2000009746"
    settings.from_title = "GENERAL SECTION"
    settings.from_organization = "Office of the Registrar General & Census Commissioner of India\nJanganana Bhawan, 2/A Man Singh Road,\nNew Delhi - 110011"
    settings.speed_post_prefix = "EN"
    settings.speed_post_suffix = "IN"
    if not settings.speed_post_start_series:
        settings.speed_post_start_series = 40000
    if not settings.speed_post_end_series:
        settings.speed_post_end_series = 50000
    if not settings.speed_post_current_number:
        settings.speed_post_current_number = 40000
    settings.save(ignore_permissions=True)
    return True

def configure_permissions():
    """Ensure Census Portal User has desk_access = 1 and only sees Census Dispatch & Census Stock"""
    if frappe.db.exists("Role", "Census Portal User"):
        role_doc = frappe.get_doc("Role", "Census Portal User")
        role_doc.desk_access = 1
        role_doc.save(ignore_permissions=True)

    # Initialize Census Stock Single DocType
    try:
        stock_doc = frappe.get_single("Census Stock")
        stock_doc.populate_live_stock()
        stock_doc.save(ignore_permissions=True)
    except Exception:
        pass
