# Census Distribution Monitoring Software

> **A Pure Frappe Framework Custom App (v15 & v16 Compatible, No ERPNext Required)**  
> Developed for tracking Census kit consignments, real-time warehouse inventory, state-wise dispatches via India Post Speed Post, barcode label printing, and customer portal monitoring.

---

## 🌟 Key Features

1. **Pure Frappe Framework (Zero ERPNext Dependency):**
   * Built entirely on Frappe Framework v15 and v16.
   * Lightweight, fast, and does not require the heavy ERPNext suite.

2. **Real-Time 24/7 Stock Monitoring:**
   * Live stock dashboard for **Enumerator Kit Sets**.
   * Live stock dashboard for all **10 Constituent Loose Items**:
     1. Water Resistant Carry Bag with Census Logo
     2. Foldable Writing Board with 2 detachable binder clips
     3. Spiral Notepad
     4. White Cap with Census Logo
     5. Lanyard for Identity Card with transparent pouch
     6. Marker Pens (Red-1 and Black-1)
     7. Ball Point Pen (Blue-1 and Black-1)
     8. Pencil
     9. Sharpener
     10. Eraser
   * Manual Stock Entry form for simple inward receipts and adjustments.

3. **India Post Speed Post Integration & Barcode Series:**
   * Pre-configured for Speed Post serial range **40000 to 50000**.
   * Automatic formatting with Prefix **`EN`** and Suffix **`IN`** (e.g. `EN000040001IN`).
   * Configurable padding, prefix, and suffix in **Census Settings**.

4. **1:1 Annexure-III Speed Post Sticker Print Format:**
   * Pixel-perfect reproduction of the **Census-2027 Project** dispatch address label.
   * Generates crisp scannable Code128 barcodes directly.
   * Pre-configured with BNPL Code `901-559`, Customer ID `2000009746`, and Janganana Bhawan New Delhi shipper address.
   * Auto-prints Box No (`1 of 2`, `2 of 2`), Weight (`12.50 Kgs`), and large bold **Unique Box No** (`1192`).

5. **Customer Portal (`/portal` or `/tracking`):**
   * **State Filter:** Select any State $\rightarrow$ automatically loads all dispatches sent to that state.
   * **Live Stock View:** Customer can check available finished kits and loose items stock at any time.
   * **Barcode / Unique Box Scanner:**
     * Works with **Handheld USB Barcode Scanners** (presses Enter automatically).
     * Works with **Smartphone / Laptop Webcams** via HTML5 scanner.
     * Manual typing supported.
   * **Instant Summary Modal:** Shows box weight, dispatch date, consignee address, kit contents list, and direct tracking link to India Post.

6. **All 36 Indian States & UTs Preloaded:**
   * Pre-populated with official Census State Codes (e.g., `Assam (18)`, `Maharashtra (27)`, `NCT of Delhi (07)`, etc.).
   * Auto-fills Director of Census Operations delivery address upon selecting the state.

---

## 📦 App Architecture & DocTypes

* **`Census Item`**: Master for Kit Set and loose items (Sr. No. 1 to 10).
* **`Census State`**: Master for all 36 States & Union Territories with Census codes and delivery addresses.
* **`Census Settings`**: Single DocType for Shipper address, BNPL code, Customer ID, and Speed Post numbering series.
* **`Census Stock Entry`**: Submittable DocType to record inward stock of kits or loose items.
* **`Census Dispatch`**: Submittable DocType to record consignments, destination states, and box breakdowns.
* **`Census Dispatch Box`**: Child table storing Box No, Unique Box No, Speed Post Barcode, and Weight.
* **`Speed Post Dispatch Label`**: Annexure-III Print Format matching official guidelines.

---

## 🚀 Installation Guide

Run the following commands inside your Frappe Bench directory:

```bash
# 1. Fetch the app from GitHub
bench get-app https://github.com/nexgenerptechnologies/Census-Distribution-Monitoring-Sofware.git

# 2. Install the app on your site
bench --site [your-site-name] install-app census_distribution_monitoring_software

# 3. Run migration to load doctypes and fixtures
bench --site [your-site-name] migrate
```

---

## ⚙️ Quick Setup & Workflow

### Step 1: Verify Settings
1. Go to **Awesomebar $\rightarrow$ Census Settings**.
2. Verify:
   * **BNPL Code No:** `901-559`
   * **Customer ID:** `2000009746`
   * **Speed Post Prefix:** `EN` | **Suffix:** `IN`
   * **Current Serial No:** `40000` (auto-increments up to 50000).

### Step 2: Add Initial Stock
1. Go to **Awesomebar $\rightarrow$ Census Stock Entry $\rightarrow$ New**.
2. Select Entry Type: **Material Receipt (Inward)**.
3. In the Items table, add:
   * **Enumerator Kit Set** $\rightarrow$ e.g. Quantity: `500`
   * (Or add any loose items with their received quantities).
4. Click **Save** and **Submit**.
5. Your stock is now live and visible on the portal!

### Step 3: Create a Dispatch Consignment
1. Go to **Awesomebar $\rightarrow$ Census Dispatch $\rightarrow$ New**.
2. Select **Destination State** (e.g., `Assam (18)`).
   * Consignee name and address auto-populate automatically.
3. In **Boxes** table, add row:
   * Speed Post serial and barcode will auto-generate from your settings!
   * Enter **Unique Box No** (e.g. `1192`).
   * Enter **Weight (Kgs)** (e.g. `12.50`).
   * Enter **Kits in Box** (e.g. `10`).
4. Click **Save** and **Submit**.

### Step 4: Print Annexure-III Box Stickers
1. On the submitted Census Dispatch, click **Print $\rightarrow$ Print All Box Labels**.
2. The print preview renders the exact Annexure-III layout with scannable Code128 barcodes ready for peel-and-stick labels.

### Step 5: Customer Portal Access
1. Create a User for your customer with role **Census Portal User**.
2. Provide them the link: `https://[your-site-domain]/portal` or `/tracking`.
3. They can:
   * Select their state to view all dispatches made.
   * See live stock levels of kits and loose items.
   * Scan any box sticker or enter the Speed Post number to view instant box contents.

---

## 📄 License
MIT License. Copyright (c) 2026 NexGen ERP Technologies.
