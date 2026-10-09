"""
Database initialization and seeding script for Lumina RFID.
Creates all schema tables and initializes clean baseline:
- 5 Cases (CASE-01 to CASE-03 functional, CASE-04 to CASE-05 inactive/future)
- Admin User (ADM001) for accessing Admin module
- Clean inventory, clean logs, clean sales, clean staff (ready for manual registration testing)
"""
import sqlite3
import os
import sys
from datetime import datetime

# Add parent dir to path so we can import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE_PATH, DATABASE_DIR

SCHEMA_SQL = """
-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'MANAGER', 'SALESPERSON')),
    section TEXT DEFAULT '',
    rfid_uid TEXT UNIQUE,
    active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Central RFID registry
CREATE TABLE IF NOT EXISTS rfid_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL UNIQUE,
    rfid_type TEXT NOT NULL CHECK(rfid_type IN ('EMPLOYEE', 'ITEM_TAG')),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'ASSIGNED', 'RELEASED')),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Cases
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    functional INTEGER NOT NULL DEFAULT 1,
    current_status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK(current_status IN ('AVAILABLE', 'ASSIGNED')),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Case assignment history
CREATE TABLE IF NOT EXISTS case_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    released_at TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'COMPLETED')),
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category TEXT DEFAULT '',
    weight TEXT DEFAULT '',
    price REAL DEFAULT 0,
    case_id TEXT,
    current_status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK(current_status IN ('AVAILABLE', 'IN_HANDLING', 'BILLING', 'SOLD')),
    current_handler_employee_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    sold_at TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- Tag assignments (RFID tag <-> product mapping history)
CREATE TABLE IF NOT EXISTS tag_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfid_uid TEXT NOT NULL,
    product_id TEXT NOT NULL,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    released_at TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'RELEASED')),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Product state history
CREATE TABLE IF NOT EXISTS product_state_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    old_state TEXT,
    new_state TEXT NOT NULL,
    employee_id TEXT,
    case_id TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    reason TEXT DEFAULT '',
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Activity logs (audit trail)
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    employee_id TEXT,
    role TEXT,
    action TEXT NOT NULL,
    case_id TEXT,
    product_id TEXT,
    rfid_uid TEXT,
    details TEXT DEFAULT ''
);

-- Sales
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT NOT NULL UNIQUE,
    product_id TEXT NOT NULL,
    employee_id TEXT,
    customer_name TEXT DEFAULT '',
    customer_phone TEXT DEFAULT '',
    amount REAL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    status TEXT NOT NULL DEFAULT 'COMPLETED',
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rfid_uid ON rfid_registry(uid);
CREATE INDEX IF NOT EXISTS idx_employees_rfid ON employees(rfid_uid);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(current_status);
CREATE INDEX IF NOT EXISTS idx_products_case ON products(case_id);
CREATE INDEX IF NOT EXISTS idx_tag_assignments_uid ON tag_assignments(rfid_uid);
CREATE INDEX IF NOT EXISTS idx_tag_assignments_product ON tag_assignments(product_id);
CREATE INDEX IF NOT EXISTS idx_case_assignments_status ON case_assignments(status);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);
"""

def init_db():
    """Create all tables with pristine clean schema."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

def seed_db():
    """Initialize clean baseline structure."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("SELECT COUNT(*) FROM cases")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    # Seed the 5 store display cases (3 functional, 2 inactive/future)
    cases = [
        ('CASE-01', 'Display Case 01', 1, 'AVAILABLE'),
        ('CASE-02', 'Display Case 02', 1, 'AVAILABLE'),
        ('CASE-03', 'Display Case 03', 1, 'AVAILABLE'),
        ('CASE-04', 'Display Case 04 (Future)', 0, 'AVAILABLE'),
        ('CASE-05', 'Display Case 05 (Future)', 0, 'AVAILABLE'),
    ]
    cur.executemany(
        "INSERT INTO cases (case_id, name, functional, current_status, created_at) VALUES (?,?,?,?,?)",
        [(c[0], c[1], c[2], c[3], now) for c in cases]
    )

    # Seed default Admin account so Admin Module can be opened
    cur.execute(
        "INSERT INTO employees (employee_id, name, role, section, rfid_uid, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        ('ADM001', 'Admin User', 'ADMIN', 'Administration', None, now, now)
    )

    # Initial system log
    cur.execute(
        "INSERT INTO activity_logs (timestamp, employee_id, role, action, details) VALUES (?,?,?,?,?)",
        (now, 'ADM001', 'ADMIN', 'SYSTEM_INITIALIZED', 'Clean database initialized. Ready for registration.')
    )

    conn.commit()
    conn.close()
    print("[INIT] Pristine database created:")
    print("  - 5 Store Cases initialized (CASE-01, CASE-02, CASE-03 functional; CASE-04, CASE-05 inactive)")
    print("  - Admin User (ADM001) initialized")
    print("  - Zero pre-registered staff, zero inventory, zero sales (100% clean slate)")

if __name__ == '__main__':
    init_db()
    seed_db()
