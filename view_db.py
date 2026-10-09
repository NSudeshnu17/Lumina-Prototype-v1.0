"""
Utility script to inspect the Lumina RFID SQLite database tables,
records, audit logs, and RFID lifecycle chains in real-time.
"""
import sqlite3
import os
import sys

# Ensure UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'database', 'jewellery.db')

def print_table(title, headers, rows):
    print(f"\n{'='*20} {title} ({len(rows)} records) {'='*20}")
    if not rows:
        print("  (No records found)")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val if val is not None else '')))
    
    header_str = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(f"  {header_str}")
    print(f"  {sep_str}")
    for row in rows:
        row_str = " | ".join(str(val if val is not None else 'NULL').ljust(col_widths[i]) for i, val in enumerate(row))
        print(f"  {row_str}")

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Cases
    cur.execute("SELECT case_id, name, functional, current_status FROM cases ORDER BY case_id")
    print_table("CASES", ["Case ID", "Name", "Functional", "Status"], cur.fetchall())

    # 2. Employees
    cur.execute("SELECT employee_id, name, role, section, rfid_uid, active FROM employees ORDER BY id")
    print_table("EMPLOYEES", ["Emp ID", "Name", "Role", "Section", "Card RFID", "Active"], cur.fetchall())

    # 3. Active & Past Case Allocations
    cur.execute("SELECT id, case_id, employee_id, assigned_at, released_at, status FROM case_assignments ORDER BY id DESC LIMIT 10")
    print_table("CASE ALLOCATIONS (Recent 10)", ["ID", "Case ID", "Employee", "Assigned At", "Released At", "Status"], cur.fetchall())

    # 4. Products
    cur.execute("SELECT product_id, product_name, category, price, case_id, current_status, current_handler_employee_id, sold_at FROM products ORDER BY id DESC LIMIT 10")
    print_table("PRODUCTS (Recent 10)", ["Product ID", "Name", "Category", "Price", "Case", "Status", "Handler", "Sold At"], cur.fetchall())

    # 5. Tag Assignments (Historical Tag Reuse Chain)
    cur.execute("SELECT id, rfid_uid, product_id, assigned_at, released_at, status FROM tag_assignments ORDER BY id DESC LIMIT 10")
    print_table("TAG ASSIGNMENT HISTORY (Recent 10)", ["ID", "RFID UID", "Product ID", "Assigned At", "Released At", "Status"], cur.fetchall())

    # 6. Sales
    cur.execute("SELECT bill_number, product_id, customer_name, customer_phone, amount, created_at FROM sales ORDER BY id DESC")
    print_table("COMPLETED SALES", ["Bill #", "Product ID", "Customer", "Phone", "Amount (₹)", "Timestamp"], cur.fetchall())

    # 7. Product State History
    cur.execute("SELECT product_id, old_state, new_state, employee_id, timestamp, reason FROM product_state_history ORDER BY id DESC LIMIT 10")
    print_table("PRODUCT STATE TRANSITIONS (Recent 10)", ["Product ID", "Old State", "New State", "Actor", "Timestamp", "Reason"], cur.fetchall())

    # 8. Activity Logs
    cur.execute("SELECT timestamp, role, action, employee_id, product_id, rfid_uid, details FROM activity_logs ORDER BY id DESC LIMIT 10")
    print_table("SYSTEM AUDIT TRAIL (Recent 10)", ["Timestamp", "Role", "Action", "Employee", "Product", "RFID", "Details"], cur.fetchall())

    conn.close()

if __name__ == '__main__':
    inspect()
