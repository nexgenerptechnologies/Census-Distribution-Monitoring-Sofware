import csv
import io
import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_stock_balance():
    """
    Returns real-time stock balances:
    - Enumerator Kit Set balance (Total Received - Total Dispatched)
    - Loose Items (Sr. No. 1 to 10) balance
    """
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

    # Inward Stock from submitted Census Stock Entry
    inward_query = """
        SELECT sei.item, SUM(sei.quantity) as total_inward
        FROM `tabCensus Stock Entry Item` sei
        INNER JOIN `tabCensus Stock Entry` se ON se.name = sei.parent
        WHERE se.docstatus = 1
        GROUP BY sei.item
    """
    inward_data = {row.item: float(row.total_inward or 0) for row in frappe.db.sql(inward_query, as_dict=True)}

    # Outward Kits from submitted Census Dispatch
    outward_kits_query = """
        SELECT SUM(total_kits) as total_kits_dispatched
        FROM `tabCensus Dispatch`
        WHERE docstatus = 1
    """
    outward_kits_result = frappe.db.sql(outward_kits_query, as_dict=True)
    kits_dispatched = float(outward_kits_result[0].total_kits_dispatched or 0) if outward_kits_result else 0.0

    # Outward loose items
    outward_loose_query = """
        SELECT di.item, SUM(di.quantity) as total_outward
        FROM `tabCensus Dispatch Item` di
        INNER JOIN `tabCensus Dispatch` d ON d.name = di.parent
        WHERE d.docstatus = 1
        GROUP BY di.item
    """
    outward_loose_data = {row.item: float(row.total_outward or 0) for row in frappe.db.sql(outward_loose_query, as_dict=True)}

    KIT_MULTIPLIERS = {
        1: 1,  # Carry Bag
        2: 1,  # Writing Board
        3: 1,  # Spiral Notepad
        4: 1,  # White Cap
        5: 1,  # Lanyard
        6: 2,  # Marker Pens (2 per Kit)
        7: 2,  # Ball Point Pens (2 per Kit)
        8: 2,  # Pencils (2 per Kit)
        9: 1,  # Sharpener
        10: 1  # Eraser
    }

    kit_inward = inward_data.get(kit_item.name, 0.0) if kit_item else 0.0
    kit_balance = max(0.0, kit_inward - kits_dispatched)

    kit_stock = {
        "item_code": kit_item.item_code if kit_item else "KIT-ENUMERATOR-01",
        "item_name": kit_item.item_name if kit_item else "Enumerator Kit Set",
        "uom": kit_item.uom if kit_item else "Set",
        "total_inward": kit_inward,
        "total_dispatched": kits_dispatched,
        "balance": kit_balance
    }

    loose_stock = []
    for item in loose_items:
        multiplier = KIT_MULTIPLIERS.get(item.sr_no, 1)
        raw_inward = inward_data.get(item.name, 0.0)
        raw_dispatched = outward_loose_data.get(item.name, 0.0)
        extra_loose = max(0.0, raw_inward - raw_dispatched)

        in_kits = kit_balance * multiplier
        total_available = in_kits + extra_loose

        total_received = (kit_inward * multiplier) + raw_inward
        total_dispatched = (kits_dispatched * multiplier) + raw_dispatched

        loose_stock.append({
            "sr_no": item.sr_no,
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty_per_kit": multiplier,
            "in_kits": in_kits,
            "extra_loose": extra_loose,
            "uom": item.uom,
            "total_inward": total_received,
            "total_dispatched": total_dispatched,
            "balance": total_available
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
    query = (query or "").strip()
    if not query:
        return {"found": False, "message": "Please enter or scan a barcode"}

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
    speed_post_tracking_url = "https://www.indiapost.gov.in/_layouts/15/dop.portal.tracking/trackconsignment.aspx"

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

@frappe.whitelist(allow_guest=False)
def get_dashboard_analytics():
    """Returns analytics data for department dashboard charts and map"""
    stock = get_stock_balance()
    kit_balance = stock.get("kit_stock", {}).get("balance", 0)
    kit_dispatched = stock.get("kit_stock", {}).get("total_dispatched", 0)

    # State-wise dispatches
    state_sql = """
        SELECT d.state, d.state_code, SUM(d.total_kits) as kits_count, COUNT(b.name) as boxes_count, SUM(b.weight_kg) as total_weight
        FROM `tabCensus Dispatch` d
        LEFT JOIN `tabCensus Dispatch Box` b ON b.parent = d.name
        WHERE d.docstatus = 1
        GROUP BY d.state
        ORDER BY kits_count DESC
    """
    state_breakdown = frappe.db.sql(state_sql, as_dict=True)

    # Status distribution
    status_sql = """
        SELECT status, COUNT(name) as count
        FROM `tabCensus Dispatch`
        WHERE docstatus = 1
        GROUP BY status
    """
    status_breakdown = {row.status: row.count for row in frappe.db.sql(status_sql, as_dict=True)}

    return {
        "kit_stock_balance": kit_balance,
        "kit_dispatched_total": kit_dispatched,
        "state_breakdown": state_breakdown,
        "status_breakdown": status_breakdown
    }

@frappe.whitelist(allow_guest=False)
def download_dispatches_csv():
    """Generates and downloads a custom CSV / Excel report of all dispatches and boxes"""
    sql = """
        SELECT 
            d.name as dispatch_id,
            d.dispatch_date,
            d.state,
            d.state_code,
            d.consignee_name,
            d.pincode,
            d.status,
            b.box_no,
            b.unique_box_no,
            b.speed_post_barcode,
            b.weight_kg,
            b.kits_count
        FROM `tabCensus Dispatch` d
        LEFT JOIN `tabCensus Dispatch Box` b ON b.parent = d.name
        WHERE d.docstatus = 1
        ORDER BY d.dispatch_date DESC, d.name DESC, b.idx ASC
    """
    rows = frappe.db.sql(sql, as_dict=True)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Dispatch ID", "Dispatch Date", "State", "State Code", "Consignee Name", 
        "Pincode", "Status", "Box No", "Unique Box No", "Speed Post Barcode", 
        "Weight (Kgs)", "Kits in Box"
    ])

    for r in rows:
        writer.writerow([
            r.dispatch_id,
            r.dispatch_date,
            r.state,
            r.state_code,
            r.consignee_name,
            r.pincode,
            r.status,
            r.box_no,
            r.unique_box_no,
            r.speed_post_barcode,
            r.weight_kg,
            r.kits_count
        ])

    frappe.response['result'] = output.getvalue()
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = 'Census_Dispatches_Report'

@frappe.whitelist(allow_guest=False)
def download_stock_csv():
    """Generates and downloads current stock balance CSV / Excel report"""
    stock = get_stock_balance()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sr. No", "Item Code", "Item Name", "UOM", "Total Received (Inward)", "Total Dispatched", "Available Stock Balance"])

    kit = stock.get("kit_stock", {})
    writer.writerow([
        0, kit.get("item_code"), kit.get("item_name"), kit.get("uom"),
        kit.get("total_inward"), kit.get("total_dispatched"), kit.get("balance")
    ])

    for it in stock.get("loose_items", []):
        writer.writerow([
            it.get("sr_no"), it.get("item_code"), it.get("item_name"), it.get("uom"),
            it.get("total_inward"), it.get("total_dispatched"), it.get("balance")
        ])

    frappe.response['result'] = output.getvalue()
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = 'Census_Stock_Report'

@frappe.whitelist(allow_guest=False)
def get_order_vs_dispatch_summary():
    """
    Returns:
    - State-wise Order vs Dispatch summary (Ordered, Dispatched, Pending, Fulfillment %)
    - Today's Dispatched kits & boxes
    - Recent Date-wise dispatches
    """
    today = frappe.utils.today()

    # Today's dispatch
    today_sql = """
        SELECT SUM(d.total_kits) as today_kits, COUNT(d.name) as today_dispatches, COUNT(b.name) as today_boxes
        FROM `tabCensus Dispatch` d
        LEFT JOIN `tabCensus Dispatch Box` b ON b.parent = d.name
        WHERE d.dispatch_date = %(today)s AND d.docstatus = 1
    """
    today_res = frappe.db.sql(today_sql, {"today": today}, as_dict=True)
    today_stats = {
        "today_kits": float(today_res[0].today_kits or 0) if today_res else 0,
        "today_dispatches": int(today_res[0].today_dispatches or 0) if today_res else 0,
        "today_boxes": int(today_res[0].today_boxes or 0) if today_res else 0,
    }

    # State-wise Orders vs Dispatches
    orders = frappe.get_all(
        "Census Order",
        fields=["name", "order_no", "state", "order_date", "ordered_kits", "dispatched_kits", "pending_kits", "completion_percent", "status"],
        order_by="order_date desc"
    )

    # Date-wise dispatches
    recent_dispatches = frappe.db.sql("""
        SELECT d.dispatch_date, d.state, d.total_kits, d.name as dispatch_id, d.consignee_name, COUNT(b.name) as boxes_count
        FROM `tabCensus Dispatch` d
        LEFT JOIN `tabCensus Dispatch Box` b ON b.parent = d.name
        WHERE d.docstatus = 1
        GROUP BY d.name
        ORDER BY d.dispatch_date DESC
        LIMIT 20
    """, as_dict=True)

    stock = get_stock_balance()

    return {
        "today_stats": today_stats,
        "orders": orders,
        "recent_dispatches": recent_dispatches,
        "stock": stock
    }
