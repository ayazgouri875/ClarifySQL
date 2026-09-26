"""
QueryMind Database Seeder
Generates mathematically consistent, high-fidelity seed data for the 10-table company database.
Produces:
1. database/seed.sql (PostgreSQL compatible)
2. database/company.db (Local SQLite database ready for immediate queries/testing)
"""

import os
import sqlite3
import random
from datetime import datetime, date, timedelta

# Fix random seed for reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_OUTPUT_PATH = os.path.join(BASE_DIR, "seed.sql")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "company.db")

# 1. Employees Data
EMPLOYEES = [
    (1, "Aarav", "Sharma", "aarav.sharma@company.com", "VP of Sales", "Executive", "2022-01-15", 185000.00, None),
    (2, "Priya", "Nair", "priya.nair@company.com", "Regional Sales Manager", "Sales", "2022-03-01", 120000.00, 1),
    (3, "Rohan", "Mehta", "rohan.mehta@company.com", "Enterprise Account Exec", "Sales", "2022-06-10", 95000.00, 2),
    (4, "Sneha", "Kulkarni", "sneha.kulkarni@company.com", "Senior Sales Rep", "Sales", "2023-02-15", 85000.00, 2),
    (5, "Vikram", "Singh", "vikram.singh@company.com", "Inside Sales Rep", "Sales", "2023-08-01", 72000.00, 2),
    (6, "Ananya", "Deshmukh", "ananya.d@company.com", "Head of Engineering", "Engineering", "2021-11-01", 175000.00, None),
    (7, "Arjun", "Patel", "arjun.patel@company.com", "DevOps Engineer", "Engineering", "2023-04-12", 90000.00, 6),
    (8, "Neha", "Gupta", "neha.gupta@company.com", "Customer Support Lead", "Support", "2022-09-20", 78000.00, None),
    (9, "Karthik", "Rao", "karthik.rao@company.com", "Product Manager", "Product", "2022-05-18", 130000.00, None),
    (10, "Divya", "Iyer", "divya.iyer@company.com", "Marketing Director", "Marketing", "2022-08-14", 140000.00, None),
]

# 2. Sales Reps Data
SALES_REPS = [
    (1, 2, "West India", 2500000.00, 0.08),
    (2, 3, "North India", 3000000.00, 0.10),
    (3, 4, "South India", 2200000.00, 0.07),
    (4, 5, "International", 3500000.00, 0.12),
]

# 3. Customers Data (30 customers across cities, segments, and signup dates)
CUSTOMERS = [
    (1, "Apex Global Logistics", "ops@apexlogistics.in", "+91-9820011223", "2024-02-10", "India", "Mumbai", "Enterprise", "Active"),
    (2, "Zenith Tech Systems", "procure@zenithtech.com", "+91-9811122334", "2024-04-15", "India", "Bengaluru", "Enterprise", "Active"),
    (3, "BlueSky Media Labs", "finance@blueskymedia.io", "+91-9833344556", "2024-08-20", "India", "Delhi", "SMB", "Active"),
    (4, "Kavita Enterprise", "kavita@kavitaent.in", "+91-9844455667", "2025-01-12", "India", "Pune", "SMB", "Active"),
    (5, "Metro Retailers Ltd", "contact@metroretailers.in", "+91-9855566778", "2025-03-05", "India", "Mumbai", "Enterprise", "Active"),
    (6, "Nova Health Sciences", "accounts@novahealth.org", "+91-9866677889", "2025-05-18", "India", "Hyderabad", "SMB", "Active"),
    (7, "OmniCorp Digital", "purchasing@omnicorp.co", "+1-212-5550199", "2025-07-22", "United States", "New York", "Enterprise", "Active"),
    (8, "Siddharth Verma", "siddharth.v@gmail.com", "+91-9877788990", "2025-09-14", "India", "Delhi", "Retail", "Active"),
    (9, "Pooja Hegde", "pooja.h89@yahoo.com", "+91-9888899001", "2025-10-02", "India", "Bengaluru", "Retail", "Active"),
    (10, "Silverline Hospitality", "procure@silverlinehotels.com", "+91-9899900112", "2025-11-28", "India", "Chennai", "SMB", "Active"),
    (11, "CloudScale Solutions", "infra@cloudscale.uk", "+44-20-79460912", "2026-01-05", "United Kingdom", "London", "Enterprise", "Active"),
    (12, "Rahul Kapoor", "rahul.kapoor@outlook.com", "+91-9900011223", "2026-02-14", "India", "Mumbai", "Retail", "Active"),
    (13, "BrightFuture Education", "admin@brightfuture.edu", "+91-9911122334", "2026-03-10", "India", "Pune", "SMB", "Active"),
    (14, "NexGen Robotics", "hardware@nexgenrobotics.sg", "+65-6789-0123", "2026-04-25", "Singapore", "Singapore", "Enterprise", "Active"),
    (15, "Amitabh Joshi", "amitabh.j@gmail.com", "+91-9922233445", "2026-05-08", "India", "Mumbai", "Retail", "Active"),
    (16, "Sunita Mehra", "sunita.m@rediffmail.com", "+91-9933344556", "2026-06-19", "India", "Delhi", "Retail", "Active"),
    (17, "Quantum FinTech", "ops@quantumfintech.in", "+91-9944455667", "2026-07-01", "India", "Hyderabad", "Enterprise", "Active"),
    # Customers signed up in August 2026 (Last Month)
    (18, "Beacon Analytics Corp", "procure@beaconanalytics.com", "+91-9955566778", "2026-08-03", "India", "Bengaluru", "Enterprise", "Active"),
    (19, "Ramesh & Sons Hardware", "ramesh@rameshhardware.in", "+91-9966677889", "2026-08-08", "India", "Ahmedabad", "SMB", "Active"),
    (20, "Alisha Fernandes", "alisha.f@gmail.com", "+91-9977788990", "2026-08-14", "India", "Mumbai", "Retail", "Active"),
    (21, "GreenWave Energies", "orders@greenwave.in", "+91-9988899001", "2026-08-21", "India", "Chennai", "SMB", "Active"),
    (22, "Deepak Chawla", "deepak.c@outlook.com", "+91-9999900112", "2026-08-27", "India", "Delhi", "Retail", "Active"),
    # Customers signed up in September 2026 (Current Month)
    (23, "Vanguard Capital", "trade@vanguardcapital.in", "+91-9810012345", "2026-09-02", "India", "Mumbai", "Enterprise", "Active"),
    (24, "Anika Sen", "anika.sen@gmail.com", "+91-9820023456", "2026-09-05", "India", "Kolkata", "Retail", "Active"),
    (25, "Pulse Medical Supplies", "info@pulsemedical.in", "+91-9830034567", "2026-09-12", "India", "Pune", "SMB", "Active"),
    # Inactive or Never-ordered customers (crucial for complex queries like 'Which customers have never placed an order?')
    (26, "Dormant Retailer Inc", "support@dormantretail.com", "+91-9840045678", "2024-05-10", "India", "Jaipur", "SMB", "Inactive"),
    (27, "Harsh Vardhan", "harsh.v@gmail.com", "+91-9850056789", "2026-08-18", "India", "Mumbai", "Retail", "Active"), # Signed up last month, never ordered!
    (28, "Tanya Batra", "tanya.b@gmail.com", "+91-9860067890", "2026-09-15", "India", "Delhi", "Retail", "Active"), # Never ordered
    (29, "Nordic Softworks", "license@nordicsoft.se", "+46-8-1234567", "2025-08-10", "Sweden", "Stockholm", "Enterprise", "Active"),
    (30, "Simran Walia", "simran.w@gmail.com", "+91-9870078901", "2026-01-20", "India", "Chandigarh", "Retail", "Suspended"),
]

# 4. Products Data (20 products across categories)
PRODUCTS = [
    (1, "UltraBook Pro 15", "Computers", "Laptops", 85000.00, 60000.00, 45, True),
    (2, "Business Workstation X9", "Computers", "Desktops", 110000.00, 78000.00, 20, True),
    (3, "ErgoDesk Pro Electric", "Furniture", "Desks", 32000.00, 19000.00, 30, True),
    (4, "Mesh Executive Chair", "Furniture", "Seating", 18500.00, 10500.00, 50, True),
    (5, "CloudSync Enterprise License (Annual)", "Software", "Cloud", 45000.00, 5000.00, 999, True),
    (6, "SecureShield Endpoint Security", "Software", "Security", 15000.00, 2000.00, 999, True),
    (7, "4K Ultra-Wide Monitor 34-inch", "Peripherals", "Monitors", 42000.00, 28000.00, 35, True),
    (8, "Wireless Mechanical Keyboard", "Peripherals", "Keyboards", 7500.00, 4200.00, 80, True),
    (9, "Precision Laser Mouse", "Peripherals", "Mice", 3800.00, 1900.00, 120, True),
    (10, "Gigabit Managed Switch 24-Port", "Networking", "Switches", 26000.00, 17000.00, 25, True),
    (11, "Wi-Fi 6 Enterprise Access Point", "Networking", "Routers", 14500.00, 9000.00, 40, True),
    (12, "Laser Multifunction Printer", "Office Equipment", "Printers", 28000.00, 18500.00, 15, True),
    (13, "Noise-Cancelling Conference Headset", "Audio", "Headsets", 12000.00, 6500.00, 60, True),
    (14, "Studio Podcast Microphone USB", "Audio", "Microphones", 8900.00, 4800.00, 45, True),
    (15, "Server Rack Cabinet 42U", "Networking", "Racks", 55000.00, 34000.00, 10, True),
    (16, "Smart UPS Battery Backup 1500VA", "Power", "UPS", 19500.00, 13000.00, 25, True),
    (17, "High-Speed Document Scanner", "Office Equipment", "Scanners", 22000.00, 14000.00, 18, True),
    (18, "USB-C Multiport Docking Station", "Accessories", "Adapters", 6500.00, 3200.00, 90, True),
    (19, "Heavy Duty Paper Shredder", "Office Equipment", "Shredders", 11500.00, 6800.00, 22, True),
    (20, "Biometric Attendance Terminal", "Security", "Access Control", 16500.00, 9500.00, 30, True),
]

def generate_orders_and_related():
    orders = []
    order_items = []
    payments = []
    shipments = []
    returns = []
    
    order_id = 1
    item_id = 1
    payment_id = 1
    shipment_id = 1
    return_id = 1
    
    # Active ordering customer IDs (exclude 26, 27, 28)
    ordering_customers = [c[0] for c in CUSTOMERS if c[0] not in (26, 27, 28)]
    
    # Specific date buckets to ensure questions like "last month" (August 2026), "this month" (Sept 2026), "this year" (2026), and 2025 work flawlessly!
    date_schedule = [
        # 2025 orders
        ("2025-03-10", 1, 1),
        ("2025-05-14", 2, 2),
        ("2025-08-20", 3, 3),
        ("2025-11-05", 5, 1),
        ("2025-12-18", 7, 4),
        # 2026 Q1
        ("2026-01-15", 1, 1),
        ("2026-02-20", 2, 2),
        ("2026-03-05", 4, 1),
        ("2026-03-22", 10, 3),
        ("2026-03-28", 11, 4),
        # 2026 Q2
        ("2026-04-12", 6, 3),
        ("2026-05-02", 7, 4),
        ("2026-05-18", 14, 4),
        ("2026-06-04", 17, 3),
        ("2026-06-25", 12, 1),
        # 2026 July
        ("2026-07-08", 2, 2),
        ("2026-07-15", 5, 1),
        ("2026-07-29", 1, 1),
        # 2026 August (LAST MONTH - rich data for "best customers last month")
        ("2026-08-02", 1, 1),   # Apex Global (Heavy buyer)
        ("2026-08-05", 7, 4),   # OmniCorp Digital (Massive enterprise purchase)
        ("2026-08-08", 2, 2),   # Zenith Tech Systems (High spending)
        ("2026-08-11", 18, 2),  # Beacon Analytics (New signup August)
        ("2026-08-14", 4, 1),   # Kavita Enterprise
        ("2026-08-16", 1, 1),   # Apex Global (Second order in Aug)
        ("2026-08-19", 14, 4),  # NexGen Robotics
        ("2026-08-22", 20, 1),  # Alisha Fernandes (Retail)
        ("2026-08-25", 1, 1),   # Apex Global (Third order in Aug)
        ("2026-08-26", 11, 4),  # CloudScale Solutions
        ("2026-08-28", 17, 3),  # Quantum FinTech
        ("2026-08-30", 19, 1),  # Ramesh & Sons Hardware
        # 2026 September (THIS MONTH)
        ("2026-09-02", 23, 1),  # Vanguard Capital
        ("2026-09-06", 1, 1),   # Apex Global
        ("2026-09-10", 7, 4),   # OmniCorp Digital
        ("2026-09-14", 2, 2),   # Zenith Tech
        ("2026-09-18", 21, 3),  # GreenWave
        ("2026-09-22", 18, 2),  # Beacon Analytics
        ("2026-09-24", 25, 1),  # Pulse Medical
    ]

    for order_date_str, cust_id, rep_id in date_schedule:
        order_date = datetime.strptime(order_date_str, "%Y-%m-%d").date()
        shipped_date = order_date + timedelta(days=random.randint(1, 3))
        
        # Decide order status
        if order_date_str >= "2026-09-20":
            status = "Processing"
            shipped_date_val = None
        else:
            status = "Completed"
            shipped_date_val = str(shipped_date)
            
        shipping_fee = 250.00 if cust_id in (8, 9, 12, 15, 16, 20, 22, 24) else 0.00
        
        # Select 1 to 4 items for this order
        num_items = random.randint(1, 4)
        if cust_id in (1, 7, 14): # Big spenders
            num_items = random.randint(3, 5)
            
        chosen_products = random.sample(PRODUCTS, num_items)
        order_total = 0.0
        
        current_order_items = []
        for p in chosen_products:
            p_id, p_name, cat, subcat, unit_price, cost, stock, active = p
            # Enterprise buys higher quantities
            if cust_id in (1, 2, 7, 11, 14, 17, 23):
                qty = random.randint(3, 12)
            else:
                qty = random.randint(1, 3)
                
            discount = round((unit_price * qty) * (0.05 if qty >= 5 else 0.0), 2)
            line_total = round((unit_price * qty) - discount, 2)
            order_total += line_total
            
            current_order_items.append((item_id, order_id, p_id, qty, unit_price, discount, line_total))
            item_id += 1
            
        order_total += shipping_fee
        order_items.extend(current_order_items)
        
        orders.append((
            order_id,
            cust_id,
            rep_id,
            order_date_str,
            str(order_date + timedelta(days=7)),
            shipped_date_val,
            status,
            round(order_total, 2),
            shipping_fee,
            "Paid"
        ))
        
        # Payment entry
        payment_methods = ["Credit Card", "UPI", "Bank Transfer", "PayPal", "Net Banking"]
        method = "Bank Transfer" if cust_id in (1, 2, 7, 11) else random.choice(payment_methods)
        payments.append((
            payment_id,
            order_id,
            f"{order_date_str} 14:30:00",
            round(order_total, 2),
            method,
            "Success",
            f"TXN-{20260000 + payment_id}"
        ))
        payment_id += 1
        
        # Shipment entry (if shipped)
        if shipped_date_val:
            carriers = ["Blue Dart", "DHL", "FedEx", "Delhivery"]
            carrier = "DHL" if cust_id in (7, 11, 14) else random.choice(carriers)
            shipments.append((
                shipment_id,
                order_id,
                carrier,
                f"TRK{90000000 + shipment_id}",
                f"{shipped_date_val} 10:00:00",
                str(order_date + timedelta(days=5)),
                f"{order_date + timedelta(days=4)} 16:00:00",
                "Delivered"
            ))
            shipment_id += 1
            
        # Occasional return (for return rate analytics)
        if order_id in (4, 11, 19):
            returned_item = current_order_items[0]
            returns.append((
                return_id,
                order_id,
                returned_item[0],
                str(order_date + timedelta(days=8)),
                "Defective item on delivery" if order_id == 4 else "Wrong size specification",
                returned_item[6], # refund line_total
                "Processed"
            ))
            return_id += 1
            
        order_id += 1

    return orders, order_items, payments, shipments, returns

def generate_visits():
    visits = []
    visit_id = 1
    sources = ["Organic Search", "Direct", "Social Media", "Paid Ads", "Email", "Referral"]
    devices = ["Desktop", "Mobile", "Tablet"]
    
    # Generate ~80 realistic visits
    # Apex Global (customer 1) visits very frequently
    # Alisha Fernandes (customer 20) visits often
    # Zenith Tech (customer 2) visits
    start_date = date(2026, 7, 1)
    for day in range(80):
        current_date = start_date + timedelta(days=day)
        date_str = str(current_date)
        
        # Multiple visits per day across different customers
        for cust_id in [1, 2, 3, 4, 5, 7, 8, 9, 12, 14, 18, 20, 23, 27]:
            if random.random() < 0.25 or (cust_id == 1 and random.random() < 0.70):
                duration = random.randint(45, 900)
                pages = max(1, duration // 70)
                visits.append((
                    visit_id,
                    cust_id,
                    f"{date_str} {random.randint(9, 21):02d}:{random.randint(10, 59):02d}:00",
                    pages,
                    duration,
                    random.choice(sources),
                    random.choice(devices)
                ))
                visit_id += 1
    return visits

def main():
    orders, order_items, payments, shipments, returns = generate_orders_and_related()
    visits = generate_visits()
    
    print(f"Generated {len(EMPLOYEES)} employees")
    print(f"Generated {len(SALES_REPS)} sales reps")
    print(f"Generated {len(CUSTOMERS)} customers")
    print(f"Generated {len(PRODUCTS)} products")
    print(f"Generated {len(orders)} orders")
    print(f"Generated {len(order_items)} order items")
    print(f"Generated {len(payments)} payments")
    print(f"Generated {len(visits)} visits")
    print(f"Generated {len(shipments)} shipments")
    print(f"Generated {len(returns)} returns")
    
    # 1. Generate seed.sql
    with open(SQL_OUTPUT_PATH, "w") as f:
        f.write("-- ==============================================================================\n")
        f.write("-- QueryMind Realistic Company Database Seed Script (PostgreSQL)\n")
        f.write("-- ==============================================================================\n\n")
        
        # Employees
        f.write("-- 1. EMPLOYEES\n")
        f.write("INSERT INTO employees (employee_id, first_name, last_name, email, role, department, hire_date, salary, manager_id) VALUES\n")
        emp_rows = [f"({e[0]}, '{e[1]}', '{e[2]}', '{e[3]}', '{e[4]}', '{e[5]}', '{e[6]}', {e[7]}, {e[8] if e[8] else 'NULL'})" for e in EMPLOYEES]
        f.write(",\n".join(emp_rows) + ";\n\n")
        
        # Sales Reps
        f.write("-- 2. SALES REPS\n")
        f.write("INSERT INTO sales_reps (sales_rep_id, employee_id, region, quota, commission_rate) VALUES\n")
        sr_rows = [f"({s[0]}, {s[1]}, '{s[2]}', {s[3]}, {s[4]})" for s in SALES_REPS]
        f.write(",\n".join(sr_rows) + ";\n\n")
        
        # Customers
        f.write("-- 3. CUSTOMERS\n")
        f.write("INSERT INTO customers (customer_id, customer_name, email, phone, signup_date, country, city, segment, status) VALUES\n")
        cust_rows = [f"({c[0]}, '{c[1]}', '{c[2]}', '{c[3]}', '{c[4]}', '{c[5]}', '{c[6]}', '{c[7]}', '{c[8]}')" for c in CUSTOMERS]
        f.write(",\n".join(cust_rows) + ";\n\n")
        
        # Products
        f.write("-- 4. PRODUCTS\n")
        f.write("INSERT INTO products (product_id, product_name, category, subcategory, unit_price, cost_price, stock_quantity, is_active) VALUES\n")
        prod_rows = [f"({p[0]}, '{p[1]}', '{p[2]}', '{p[3]}', {p[4]}, {p[5]}, {p[6]}, {p[7]})" for p in PRODUCTS]
        f.write(",\n".join(prod_rows) + ";\n\n")
        
        # Orders
        f.write("-- 5. ORDERS\n")
        f.write("INSERT INTO orders (order_id, customer_id, sales_rep_id, order_date, required_date, shipped_date, status, total_amount, shipping_fee, payment_status) VALUES\n")
        ord_rows = [f"({o[0]}, {o[1]}, {o[2]}, '{o[3]}', '{o[4]}', {f"'{o[5]}'" if o[5] else 'NULL'}, '{o[6]}', {o[7]}, {o[8]}, '{o[9]}')" for o in orders]
        f.write(",\n".join(ord_rows) + ";\n\n")
        
        # Order Items
        f.write("-- 6. ORDER ITEMS\n")
        f.write("INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount, line_total) VALUES\n")
        item_rows = [f"({i[0]}, {i[1]}, {i[2]}, {i[3]}, {i[4]}, {i[5]}, {i[6]})" for i in order_items]
        f.write(",\n".join(item_rows) + ";\n\n")
        
        # Payments
        f.write("-- 7. PAYMENTS\n")
        f.write("INSERT INTO payments (payment_id, order_id, payment_date, amount, payment_method, status, transaction_ref) VALUES\n")
        pay_rows = [f"({p[0]}, {p[1]}, '{p[2]}', {p[3]}, '{p[4]}', '{p[5]}', '{p[6]}')" for p in payments]
        f.write(",\n".join(pay_rows) + ";\n\n")
        
        # Visits
        f.write("-- 8. VISITS\n")
        f.write("INSERT INTO visits (visit_id, customer_id, visit_date, page_views, duration_seconds, traffic_source, device) VALUES\n")
        vis_rows = [f"({v[0]}, {v[1]}, '{v[2]}', {v[3]}, {v[4]}, '{v[5]}', '{v[6]}')" for v in visits]
        f.write(",\n".join(vis_rows) + ";\n\n")
        
        # Shipments
        f.write("-- 9. SHIPMENTS\n")
        f.write("INSERT INTO shipments (shipment_id, order_id, carrier, tracking_number, shipped_date, estimated_delivery, actual_delivery, status) VALUES\n")
        ship_rows = [f"({s[0]}, {s[1]}, '{s[2]}', '{s[3]}', '{s[4]}', '{s[5]}', '{s[6]}', '{s[7]}')" for s in shipments]
        f.write(",\n".join(ship_rows) + ";\n\n")
        
        # Returns
        f.write("-- 10. RETURNS\n")
        f.write("INSERT INTO returns (return_id, order_id, order_item_id, return_date, reason, refund_amount, status) VALUES\n")
        ret_rows = [f"({r[0]}, {r[1]}, {r[2]}, '{r[3]}', '{r[4]}', {r[5]}, '{r[6]}')" for r in returns]
        f.write(",\n".join(ret_rows) + ";\n\n")
        
        # Reset sequence counters for PostgreSQL SERIAL columns
        f.write("-- SEQUENCE SYNCHRONIZATION\n")
        f.write("SELECT setval('employees_employee_id_seq', (SELECT MAX(employee_id) FROM employees));\n")
        f.write("SELECT setval('sales_reps_sales_rep_id_seq', (SELECT MAX(sales_rep_id) FROM sales_reps));\n")
        f.write("SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers));\n")
        f.write("SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products));\n")
        f.write("SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders));\n")
        f.write("SELECT setval('order_items_order_item_id_seq', (SELECT MAX(order_item_id) FROM order_items));\n")
        f.write("SELECT setval('payments_payment_id_seq', (SELECT MAX(payment_id) FROM payments));\n")
        f.write("SELECT setval('visits_visit_id_seq', (SELECT MAX(visit_id) FROM visits));\n")
        f.write("SELECT setval('shipments_shipment_id_seq', (SELECT MAX(shipment_id) FROM shipments));\n")
        f.write("SELECT setval('returns_return_id_seq', (SELECT MAX(return_id) FROM returns));\n")

    print(f"Successfully generated {SQL_OUTPUT_PATH}")

    # 2. Build local SQLite database for instant zero-dependency execution
    if os.path.exists(SQLITE_DB_PATH):
        os.remove(SQLITE_DB_PATH)
        
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()
    
    # SQLite schema
    cur.executescript("""
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        department TEXT NOT NULL,
        hire_date TEXT NOT NULL,
        salary REAL NOT NULL,
        manager_id INTEGER REFERENCES employees(employee_id)
    );
    CREATE TABLE sales_reps (
        sales_rep_id INTEGER PRIMARY KEY,
        employee_id INTEGER NOT NULL UNIQUE REFERENCES employees(employee_id),
        region TEXT NOT NULL,
        quota REAL NOT NULL,
        commission_rate REAL NOT NULL
    );
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        signup_date TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        segment TEXT NOT NULL DEFAULT 'Retail',
        status TEXT NOT NULL DEFAULT 'Active'
    );
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT NOT NULL,
        unit_price REAL NOT NULL,
        cost_price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
        sales_rep_id INTEGER REFERENCES sales_reps(sales_rep_id),
        order_date TEXT NOT NULL,
        required_date TEXT,
        shipped_date TEXT,
        status TEXT NOT NULL DEFAULT 'Completed',
        total_amount REAL NOT NULL DEFAULT 0.0,
        shipping_fee REAL NOT NULL DEFAULT 0.0,
        payment_status TEXT NOT NULL DEFAULT 'Paid'
    );
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(product_id),
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount REAL NOT NULL DEFAULT 0.0,
        line_total REAL NOT NULL
    );
    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        payment_date TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Success',
        transaction_ref TEXT UNIQUE
    );
    CREATE TABLE visits (
        visit_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        visit_date TEXT NOT NULL,
        page_views INTEGER NOT NULL DEFAULT 1,
        duration_seconds INTEGER NOT NULL DEFAULT 60,
        traffic_source TEXT NOT NULL,
        device TEXT NOT NULL
    );
    CREATE TABLE shipments (
        shipment_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        carrier TEXT NOT NULL,
        tracking_number TEXT UNIQUE NOT NULL,
        shipped_date TEXT,
        estimated_delivery TEXT,
        actual_delivery TEXT,
        status TEXT NOT NULL DEFAULT 'Delivered'
    );
    CREATE TABLE returns (
        return_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        order_item_id INTEGER REFERENCES order_items(order_item_id),
        return_date TEXT NOT NULL,
        reason TEXT NOT NULL,
        refund_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Processed'
    );
    """)

    cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?)", EMPLOYEES)
    cur.executemany("INSERT INTO sales_reps VALUES (?,?,?,?,?)", SALES_REPS)
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)", CUSTOMERS)
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], 1 if p[7] else 0) for p in PRODUCTS])
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?,?)", order_items)
    cur.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?)", payments)
    cur.executemany("INSERT INTO visits VALUES (?,?,?,?,?,?,?)", visits)
    cur.executemany("INSERT INTO shipments VALUES (?,?,?,?,?,?,?,?)", shipments)
    cur.executemany("INSERT INTO returns VALUES (?,?,?,?,?,?,?)", returns)
    
    conn.commit()
    conn.close()
    print(f"Successfully created and seeded SQLite database: {SQLITE_DB_PATH}")

if __name__ == "__main__":
    main()
