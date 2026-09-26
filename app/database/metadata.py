"""
Schema Metadata and Business Knowledge Graph for QueryMind.
Provides structured information about tables, columns, foreign keys,
and common business synonyms used for schema grounding and intent extraction.
"""

from typing import Dict, List, Any

SCHEMA_METADATA: Dict[str, Any] = {
    "tables": {
        "employees": {
            "description": "Company personnel across sales, engineering, executive, and support departments.",
            "primary_key": "employee_id",
            "columns": {
                "employee_id": {"type": "INTEGER", "description": "Unique identifier for employee"},
                "first_name": {"type": "VARCHAR(50)", "description": "First name"},
                "last_name": {"type": "VARCHAR(50)", "description": "Last name"},
                "email": {"type": "VARCHAR(100)", "description": "Work email address"},
                "role": {"type": "VARCHAR(50)", "description": "Job designation (e.g. VP of Sales, Devops Engineer)"},
                "department": {"type": "VARCHAR(50)", "description": "Department: Executive, Sales, Engineering, Support, Product, Marketing"},
                "hire_date": {"type": "DATE", "description": "Date when employee joined the company"},
                "salary": {"type": "NUMERIC(10,2)", "description": "Monthly or annual base salary in INR/USD"},
                "manager_id": {"type": "INTEGER", "description": "Self-referencing foreign key to manager's employee_id"}
            },
            "foreign_keys": [
                {"column": "manager_id", "references_table": "employees", "references_column": "employee_id"}
            ],
            "synonyms": ["staff", "workers", "team", "personnel", "workforce"]
        },
        "sales_reps": {
            "description": "Sales representatives managing regional enterprise/SMB territories and quotas.",
            "primary_key": "sales_rep_id",
            "columns": {
                "sales_rep_id": {"type": "INTEGER", "description": "Unique identifier for sales rep"},
                "employee_id": {"type": "INTEGER", "description": "References employees.employee_id"},
                "region": {"type": "VARCHAR(50)", "description": "Sales region: North India, West India, South India, International"},
                "quota": {"type": "NUMERIC(12,2)", "description": "Annual sales revenue quota target"},
                "commission_rate": {"type": "NUMERIC(4,2)", "description": "Commission percentage (e.g. 0.08 = 8%)"}
            },
            "foreign_keys": [
                {"column": "employee_id", "references_table": "employees", "references_column": "employee_id"}
            ],
            "synonyms": ["agents", "account managers", "sellers", "reps"]
        },
        "customers": {
            "description": "Business clients (Enterprise, SMB) and retail individual consumers.",
            "primary_key": "customer_id",
            "columns": {
                "customer_id": {"type": "INTEGER", "description": "Unique customer ID"},
                "customer_name": {"type": "VARCHAR(100)", "description": "Full name of customer or business entity"},
                "email": {"type": "VARCHAR(100)", "description": "Contact email"},
                "phone": {"type": "VARCHAR(25)", "description": "Phone number"},
                "signup_date": {"type": "DATE", "description": "Account registration date"},
                "country": {"type": "VARCHAR(50)", "description": "Country of residence or company registration"},
                "city": {"type": "VARCHAR(50)", "description": "City location (e.g. Mumbai, Delhi, Bengaluru, London)"},
                "segment": {"type": "VARCHAR(30)", "description": "Customer tier: Retail, SMB, Enterprise"},
                "status": {"type": "VARCHAR(20)", "description": "Account status: Active, Inactive, Suspended"}
            },
            "foreign_keys": [],
            "synonyms": ["clients", "buyers", "accounts", "users", "patrons"]
        },
        "products": {
            "description": "Catalog of hardware, software, office furniture, networking, and audio gear.",
            "primary_key": "product_id",
            "columns": {
                "product_id": {"type": "INTEGER", "description": "Unique product code"},
                "product_name": {"type": "VARCHAR(120)", "description": "Product title/model name"},
                "category": {"type": "VARCHAR(50)", "description": "Top-level category: Computers, Furniture, Software, Peripherals, Networking, Audio, Office Equipment, Power, Security, Accessories"},
                "subcategory": {"type": "VARCHAR(50)", "description": "Subcategory: Laptops, Desks, Cloud, Monitors, Keyboards, Switches, Routers, etc."},
                "unit_price": {"type": "NUMERIC(10,2)", "description": "Selling price per item"},
                "cost_price": {"type": "NUMERIC(10,2)", "description": "Procurement/cost price per item for profit margin analysis"},
                "stock_quantity": {"type": "INTEGER", "description": "Available inventory in warehouse"},
                "is_active": {"type": "BOOLEAN", "description": "Whether product is active for purchase"}
            },
            "foreign_keys": [],
            "synonyms": ["items", "inventory", "goods", "catalog", "merchandise"]
        },
        "orders": {
            "description": "Customer purchase orders, tracking order totals, order status, and dates.",
            "primary_key": "order_id",
            "columns": {
                "order_id": {"type": "INTEGER", "description": "Unique order ID"},
                "customer_id": {"type": "INTEGER", "description": "References customers.customer_id"},
                "sales_rep_id": {"type": "INTEGER", "description": "References sales_reps.sales_rep_id (nullable for retail direct orders)"},
                "order_date": {"type": "DATE", "description": "Date order was placed"},
                "required_date": {"type": "DATE", "description": "Target delivery date requested"},
                "shipped_date": {"type": "DATE", "description": "Actual date shipment departed warehouse"},
                "status": {"type": "VARCHAR(20)", "description": "Order fulfillment status: Completed, Processing, Cancelled, Shipped, Delivered"},
                "total_amount": {"type": "NUMERIC(12,2)", "description": "Gross invoice total including items and shipping"},
                "shipping_fee": {"type": "NUMERIC(8,2)", "description": "Delivery charge billed"},
                "payment_status": {"type": "VARCHAR(20)", "description": "Payment state: Paid, Pending, Failed, Refunded"}
            },
            "foreign_keys": [
                {"column": "customer_id", "references_table": "customers", "references_column": "customer_id"},
                {"column": "sales_rep_id", "references_table": "sales_reps", "references_column": "sales_rep_id"}
            ],
            "synonyms": ["purchases", "sales", "transactions", "deals", "invoices"]
        },
        "order_items": {
            "description": "Line items breakdown inside each order.",
            "primary_key": "order_item_id",
            "columns": {
                "order_item_id": {"type": "INTEGER", "description": "Unique line item ID"},
                "order_id": {"type": "INTEGER", "description": "References orders.order_id"},
                "product_id": {"type": "INTEGER", "description": "References products.product_id"},
                "quantity": {"type": "INTEGER", "description": "Number of units ordered"},
                "unit_price": {"type": "NUMERIC(10,2)", "description": "Unit selling price at time of order"},
                "discount": {"type": "NUMERIC(5,2)", "description": "Flat discount amount applied to this line"},
                "line_total": {"type": "NUMERIC(12,2)", "description": "Net amount: (quantity * unit_price) - discount"}
            },
            "foreign_keys": [
                {"column": "order_id", "references_table": "orders", "references_column": "order_id"},
                {"column": "product_id", "references_table": "products", "references_column": "product_id"}
            ],
            "synonyms": ["line items", "cart items", "order details", "purchased products"]
        },
        "payments": {
            "description": "Settled and pending financial transactions for orders.",
            "primary_key": "payment_id",
            "columns": {
                "payment_id": {"type": "INTEGER", "description": "Unique payment record ID"},
                "order_id": {"type": "INTEGER", "description": "References orders.order_id"},
                "payment_date": {"type": "TIMESTAMP", "description": "Timestamp when payment was processed"},
                "amount": {"type": "NUMERIC(12,2)", "description": "Cash/fund amount processed"},
                "payment_method": {"type": "VARCHAR(30)", "description": "Payment mode: Credit Card, UPI, Bank Transfer, PayPal, Net Banking"},
                "status": {"type": "VARCHAR(20)", "description": "Transaction status: Success, Pending, Failed"},
                "transaction_ref": {"type": "VARCHAR(100)", "description": "Unique banking gateway reference"}
            },
            "foreign_keys": [
                {"column": "order_id", "references_table": "orders", "references_column": "order_id"}
            ],
            "synonyms": ["settlements", "receipts", "collections", "cash flow"]
        },
        "visits": {
            "description": "Website sessions tracking customer traffic, duration, device, and frequency.",
            "primary_key": "visit_id",
            "columns": {
                "visit_id": {"type": "INTEGER", "description": "Unique session ID"},
                "customer_id": {"type": "INTEGER", "description": "References customers.customer_id (nullable for guests)"},
                "visit_date": {"type": "TIMESTAMP", "description": "Session start timestamp"},
                "page_views": {"type": "INTEGER", "description": "Number of pages viewed in session"},
                "duration_seconds": {"type": "INTEGER", "description": "Total length of browsing session in seconds"},
                "traffic_source": {"type": "VARCHAR(50)", "description": "Channel: Organic Search, Direct, Social Media, Paid Ads, Email, Referral"},
                "device": {"type": "VARCHAR(30)", "description": "Client device: Desktop, Mobile, Tablet"}
            },
            "foreign_keys": [
                {"column": "customer_id", "references_table": "customers", "references_column": "customer_id"}
            ],
            "synonyms": ["sessions", "web traffic", "clicks", "site activity", "page views", "engagement"]
        },
        "shipments": {
            "description": "Logistics tracking for physical order delivery.",
            "primary_key": "shipment_id",
            "columns": {
                "shipment_id": {"type": "INTEGER", "description": "Unique dispatch shipment ID"},
                "order_id": {"type": "INTEGER", "description": "References orders.order_id"},
                "carrier": {"type": "VARCHAR(50)", "description": "Courier company: Blue Dart, DHL, FedEx, UPS, Delhivery"},
                "tracking_number": {"type": "VARCHAR(100)", "description": "Waybill/tracking number"},
                "shipped_date": {"type": "TIMESTAMP", "description": "Departure timestamp"},
                "estimated_delivery": {"type": "DATE", "description": "Promised delivery date"},
                "actual_delivery": {"type": "TIMESTAMP", "description": "Actual delivery timestamp at customer doorstep"},
                "status": {"type": "VARCHAR(30)", "description": "Delivery status: In Transit, Delivered, Delayed, Returned"}
            },
            "foreign_keys": [
                {"column": "order_id", "references_table": "orders", "references_column": "order_id"}
            ],
            "synonyms": ["deliveries", "dispatches", "logistics", "consignments"]
        },
        "returns": {
            "description": "Product return requests and refund tracking.",
            "primary_key": "return_id",
            "columns": {
                "return_id": {"type": "INTEGER", "description": "Unique return authorization ID"},
                "order_id": {"type": "INTEGER", "description": "References orders.order_id"},
                "order_item_id": {"type": "INTEGER", "description": "References order_items.order_item_id"},
                "return_date": {"type": "DATE", "description": "Date return was submitted"},
                "reason": {"type": "VARCHAR(200)", "description": "Reason: Defective item, Wrong size, Not as described, etc."},
                "refund_amount": {"type": "NUMERIC(10,2)", "description": "Amount refunded to customer"},
                "status": {"type": "VARCHAR(30)", "description": "Status: Requested, Approved, Processed, Rejected"}
            },
            "foreign_keys": [
                {"column": "order_id", "references_table": "orders", "references_column": "order_id"},
                {"column": "order_item_id", "references_table": "order_items", "references_column": "order_item_id"}
            ],
            "synonyms": ["refunds", "rma", "exchanges", "reversals"]
        }
    }
}

def get_compact_schema_prompt() -> str:
    """Formats the database schema into a clean, concise prompt representation for the LLM."""
    lines = ["DATABASE SCHEMA (Relational Tables & Columns):"]
    for table_name, meta in SCHEMA_METADATA["tables"].items():
        cols = []
        for col_name, col_info in meta["columns"].items():
            cols.append(f"{col_name} ({col_info['type']})")
        lines.append(f"\nTABLE {table_name}:")
        lines.append(f"  Description: {meta['description']}")
        lines.append(f"  Columns: {', '.join(cols)}")
        if meta["foreign_keys"]:
            fk_strs = [f"{fk['column']} -> {fk['references_table']}.{fk['references_column']}" for fk in meta["foreign_keys"]]
            lines.append(f"  Foreign Keys: {', '.join(fk_strs)}")
    return "\n".join(lines)

def get_table_names() -> List[str]:
    """Returns list of valid table names."""
    return list(SCHEMA_METADATA["tables"].keys())

def get_columns_for_table(table_name: str) -> List[str]:
    """Returns valid column names for a given table."""
    table = SCHEMA_METADATA["tables"].get(table_name)
    if table:
        return list(table["columns"].keys())
    return []
