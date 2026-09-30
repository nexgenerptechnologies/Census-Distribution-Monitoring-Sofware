import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_stock_balance():
    """
    Returns real-time stock balances:
    - Enumerator Kit Set balance (Total Received - Total Dispatched)
    - Loose Items (Sr. No. 1 to 10) balance
    """
    # 1. Fetch all items
    items = frappe.get_all(
        "Census Item",
        fields=["name", "item_code", "item_name", "sr_no", "is_kit_set", "uom"],
        order_by="sr_no asc"
    )

    kit_item = None
    loose_items = []
    item_map = {}

    for item in items:
        item_map[item.name] = item
        if item.is_kit_set:
            kit_item = item
        else:
            loose_items.append(item)

    # 2. Inward Stock from submitted Census Stock Entry
    inward_query = """
        SELECT sei.item, SUM(sei.quantity) as total_inward
        FROM `tabCensus Stock Entry Item` sei
        INNER JOIN `tabCensus Stock Entry` se ON se.name = sei.parent
        WHERE se.docstatus = 1
        GROUP BY sei.item
    """
    inward_data = {row.item: float(row.total_inward or 0) for row in frappe.db.sql(inward_query, as_dict=True)}

    # 3. Outward Kits from submitted Census Dispatch
    outward_kits_query = """
        SELECT SUM(total_kits) as total_kits_dispatched
        FROM `tabCensus Dispatch`
        WHERE docstatus = 1
    """
    outward_kits_result = frappe.db.sql(outward_kits_query, as_dict=True)
    kits_dispatched = float(outward_kits_result[0].total_kits_dispatched or 0) if outward_kits_result else 0.0

    # 4. Outward loose items (if specifically dispatched in items child table)
    outward_loose_query = """
        SELECT di.item, SUM(di.quantity) as total_outward
        FROM `tabCensus Dispatch Item` di
        INNER JOIN `tabCensus Dispatch` d ON d.name = di.parent
        WHERE d.docstatus = 1
        GROUP BY di.item
    """
    outward_loose_data = {row.item: float(row.total_outward or 0) for row in frappe.db.sql(outward_loose_query, as_dict=True)}

    # Assemble response
    kit_inward = inward_data.get(kit_item.name, 0.0) if kit_item else 0.0
    kit_balance = kit_inward - kits_dispatched

    kit_stock = {
        "item_code": kit_item.item_code if kit_item else "KIT-ENUMERATOR-01",
        "item_name": kit_item.item_name if kit_item else "Enumerator Kit Set",
        "uom": kit_item.uom if kit_item else "Set",
        "total_inward": kit_inward,
        "total_dispatched": kits_dispatched,
        "balance": max(0.0, kit_balance)
    }

    loose_stock = []
    for item in loose_items:
        inward_qty = inward_data.get(item.name, 0.0)
        outward_qty = outward_loose_data.get(item.name, 0.0)
        loose_stock.append({
            "sr_no": item.sr_no,
            "item_code": item.item_code,
            "item_name": item.item_name,
            "uom": item.uom,
            "total_inward": inward_qty,
            "total_dispatched": outward_qty,
            "balance": max(0.0, inward_qty - outward_qty)
        })

    return {
        "kit_stock": kit_stock,
        "loose_items": loose_stock
    }

@frappe.whitelist(allow_guest=False)
def get_states():
    """Returns list of all states for dropdown filtering"""
    return frappe.get_all(
        "Census State",
        fields=["name", "display_name", "state_name", "state_code", "consignee_name", "delivery_address", "pincode"],
        order_by="state_code asc"
    )

@frappe.whitelist(allow_guest=False)
def get_dispatches_by_state(state=None):
    """Returns list of dispatches, optionally filtered by state"""
    filters = {"docstatus": ["in", [0, 1]]}
    if state:
        filters["state"] = state

    dispatches = frappe.get_all(
        "Census Dispatch",
        filters=filters,
        fields=["name", "dispatch_date", "state", "state_code", "consignee_name", "status", "total_kits", "total_boxes", "total_weight_kg", "docstatus"],
        order_by="dispatch_date desc, creation desc"
    )

    for d in dispatches:
        d["boxes"] = frappe.get_all(
            "Census Dispatch Box",
            filters={"parent": d.name},
            fields=["box_no", "unique_box_no", "speed_post_serial", "speed_post_barcode", "weight_kg", "kits_count", "item_description", "status"]
        )

    return dispatches

@frappe.whitelist(allow_guest=False)
def lookup_barcode(query):
    """
    Search by Speed Post Barcode (e.g. EN650541929IN) or Unique Box No (e.g. 1192)
    Returns full box & dispatch summary.
    """
    query = (query or "").strip()
    if not query:
        return {"found": False, "message": "Please enter or scan a barcode"}

    # Search in boxes
    matched_box = frappe.db.sql("""
        SELECT b.*, d.name as dispatch_id, d.dispatch_date, d.state, d.state_code, 
               d.consignee_name, d.delivery_address, d.pincode, d.status as dispatch_status,
               d.total_boxes, d.total_kits
        FROM `tabCensus Dispatch Box` b
        INNER JOIN `tabCensus Dispatch` d ON d.name = b.parent
        WHERE b.speed_post_barcode = %(query)s 
           OR b.unique_box_no = %(query)s
           OR b.speed_post_serial = %(query)s
           OR d.name = %(query)s
        ORDER BY d.creation DESC
        LIMIT 1
    """, {"query": query}, as_dict=True)

    if not matched_box:
        return {
            "found": False, 
            "message": f"No dispatch record found for Barcode / Box No: {query}"
        }

    box_data = matched_box[0]
    
    # India Post tracking direct url
    speed_post_code = box_data.get("speed_post_barcode")
    speed_post_tracking_url = f"https://www.indiapost.gov.in/_layouts/15/dop.portal.tracking/trackconsignment.aspx"

    # Kit Items list for reference (Sr. No. 1 to 10)
    items_list = frappe.get_all(
        "Census Item",
        filters={"is_kit_set": 0},
        fields=["sr_no", "item_name", "uom"],
        order_by="sr_no asc"
    )

    return {
        "found": True,
        "box": box_data,
        "speed_post_tracking_url": speed_post_tracking_url,
        "kit_items": items_list
    }

@frappe.whitelist(allow_guest=True)
def get_barcode_svg_html(code):
    """Generate inline SVG barcode for Code128 scannable barcode"""
    try:
        import barcode
        from barcode.writer import SVGWriter
        import io
        
        code128 = barcode.get("code128", code, writer=SVGWriter())
        buffer = io.BytesIO()
        code128.write(buffer, options={"write_text": False, "module_height": 14.0, "module_width": 0.35, "quiet_zone": 2.0})
        svg_str = buffer.getvalue().decode("utf-8")
        return svg_str
    except Exception as e:
        return ""
