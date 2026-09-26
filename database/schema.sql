-- ==============================================================================
-- QueryMind: Ambiguity-Aware Natural Language to SQL System
-- Database Schema Definition (PostgreSQL 14+ / Standard SQL Compatible)
-- ==============================================================================

-- Drop tables in reverse dependency order if rebuilding
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS visits CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sales_reps CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

-- 1. EMPLOYEES
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    manager_id INT REFERENCES employees(employee_id)
);

COMMENT ON TABLE employees IS 'Company staff members across sales, marketing, engineering, and support';
COMMENT ON COLUMN employees.salary IS 'Monthly or annual base salary in INR / USD';

-- 2. SALES REPRESENTATIVES
CREATE TABLE sales_reps (
    sales_rep_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id),
    region VARCHAR(50) NOT NULL,
    quota NUMERIC(12, 2) NOT NULL CHECK (quota >= 0),
    commission_rate NUMERIC(4, 2) NOT NULL CHECK (commission_rate BETWEEN 0 AND 0.50)
);

COMMENT ON TABLE sales_reps IS 'Sales representatives managing corporate accounts and territory sales quotas';

-- 3. CUSTOMERS
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(25),
    signup_date DATE NOT NULL,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    segment VARCHAR(30) NOT NULL DEFAULT 'Retail' CHECK (segment IN ('Retail', 'SMB', 'Enterprise')),
    status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

COMMENT ON TABLE customers IS 'Business clients and individual consumers purchasing products';
COMMENT ON COLUMN customers.signup_date IS 'Date when the customer profile was created';
COMMENT ON COLUMN customers.segment IS 'Customer tier: Retail, SMB, or Enterprise';

-- 4. PRODUCTS
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    cost_price NUMERIC(10, 2) NOT NULL CHECK (cost_price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE products IS 'Catalog of hardware, software licenses, accessories, and office equipment';
COMMENT ON COLUMN products.unit_price IS 'Catalog selling price per unit';
COMMENT ON COLUMN products.cost_price IS 'Procurement/manufacturing cost per unit (used for profit calculations)';

-- 5. ORDERS
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    sales_rep_id INT REFERENCES sales_reps(sales_rep_id),
    order_date DATE NOT NULL,
    required_date DATE,
    shipped_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Completed' CHECK (status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Completed', 'Cancelled')),
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    shipping_fee NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_fee >= 0),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Paid' CHECK (payment_status IN ('Pending', 'Paid', 'Failed', 'Refunded'))
);

COMMENT ON TABLE orders IS 'Customer purchase orders with fulfillment tracking and sales rep association';
COMMENT ON COLUMN orders.total_amount IS 'Total gross monetary value of the order inclusive of items and discounts';

-- 6. ORDER ITEMS
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0),
    line_total NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0)
);

COMMENT ON TABLE order_items IS 'Line item details for each product in an order';
COMMENT ON COLUMN order_items.line_total IS 'Net line amount: (quantity * unit_price) - discount';

-- 7. PAYMENTS
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    payment_date TIMESTAMP NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('Credit Card', 'UPI', 'Bank Transfer', 'PayPal', 'Net Banking')),
    status VARCHAR(20) NOT NULL DEFAULT 'Success' CHECK (status IN ('Success', 'Pending', 'Failed')),
    transaction_ref VARCHAR(100) UNIQUE
);

COMMENT ON TABLE payments IS 'Financial transactions recorded against orders';
COMMENT ON COLUMN payments.amount IS 'Cash amount processed in the payment transaction';

-- 8. VISITS
CREATE TABLE visits (
    visit_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    visit_date TIMESTAMP NOT NULL,
    page_views INT NOT NULL DEFAULT 1 CHECK (page_views >= 1),
    duration_seconds INT NOT NULL DEFAULT 60 CHECK (duration_seconds >= 0),
    traffic_source VARCHAR(50) NOT NULL CHECK (traffic_source IN ('Organic Search', 'Direct', 'Social Media', 'Paid Ads', 'Email', 'Referral')),
    device VARCHAR(30) NOT NULL CHECK (device IN ('Desktop', 'Mobile', 'Tablet'))
);

COMMENT ON TABLE visits IS 'Web analytics sessions tracking customer platform engagement and frequency';
COMMENT ON COLUMN visits.duration_seconds IS 'Length of session on website/portal in seconds';

-- 9. SHIPMENTS
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    carrier VARCHAR(50) NOT NULL CHECK (carrier IN ('Blue Dart', 'DHL', 'FedEx', 'UPS', 'Delhivery')),
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    shipped_date TIMESTAMP,
    estimated_delivery DATE,
    actual_delivery TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'Delivered' CHECK (status IN ('Processing', 'In Transit', 'Delivered', 'Delayed', 'Returned'))
);

COMMENT ON TABLE shipments IS 'Logistics and delivery tracking for fulfillment operations';

-- 10. RETURNS
CREATE TABLE returns (
    return_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    order_item_id INT REFERENCES order_items(order_item_id),
    return_date DATE NOT NULL,
    reason VARCHAR(200) NOT NULL,
    refund_amount NUMERIC(10, 2) NOT NULL CHECK (refund_amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Processed' CHECK (status IN ('Requested', 'Approved', 'Processed', 'Rejected'))
);

COMMENT ON TABLE returns IS 'Merchandise returns, defective claims, and refund processing';

-- ==============================================================================
-- INDEXES FOR QUERY OPTIMIZATION AND HIGH PERFORMANCE JOINS
-- ==============================================================================
CREATE INDEX idx_customers_signup ON customers(signup_date);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_segment ON customers(segment);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_sales_rep ON orders(sales_rep_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_date ON payments(payment_date);

CREATE INDEX idx_visits_customer ON visits(customer_id);
CREATE INDEX idx_visits_date ON visits(visit_date);

CREATE INDEX idx_returns_order ON returns(order_id);
