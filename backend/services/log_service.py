"""Log service — activity and audit trail queries."""
from database.db import get_db, dicts_from_rows

def get_activity_logs(limit=100, action=None, employee_id=None):
    """Get activity logs with optional filters."""
    db = get_db()
    try:
        query = "SELECT * FROM activity_logs WHERE 1=1"
        params = []
        if action:
            query += " AND action=?"
            params.append(action)
        if employee_id:
            query += " AND employee_id=?"
            params.append(employee_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        return dicts_from_rows(db.execute(query, params).fetchall())
    finally:
        db.close()

def get_dashboard_stats():
    """Get overall stats for manager dashboard."""
    db = get_db()
    try:
        stats = {}
        stats['total_cases'] = db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        stats['functional_cases'] = db.execute("SELECT COUNT(*) FROM cases WHERE functional=1").fetchone()[0]
        stats['inactive_cases'] = db.execute("SELECT COUNT(*) FROM cases WHERE functional=0").fetchone()[0]
        stats['assigned_cases'] = db.execute("SELECT COUNT(*) FROM case_assignments WHERE status='ACTIVE'").fetchone()[0]
        stats['available_cases'] = stats['functional_cases'] - stats['assigned_cases']

        # Logged in employees (those with active case assignments)
        stats['logged_in_employees'] = db.execute(
            "SELECT COUNT(DISTINCT employee_id) FROM case_assignments WHERE status='ACTIVE'"
        ).fetchone()[0]

        stats['total_products'] = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        stats['available_products'] = db.execute("SELECT COUNT(*) FROM products WHERE current_status='AVAILABLE'").fetchone()[0]
        stats['in_handling_products'] = db.execute("SELECT COUNT(*) FROM products WHERE current_status='IN_HANDLING'").fetchone()[0]
        stats['billing_products'] = db.execute("SELECT COUNT(*) FROM products WHERE current_status='BILLING'").fetchone()[0]
        stats['sold_products'] = db.execute("SELECT COUNT(*) FROM products WHERE current_status='SOLD'").fetchone()[0]
        stats['total_sales'] = db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        stats['unresolved_items'] = stats['in_handling_products'] + stats['billing_products']

        return stats
    finally:
        db.close()
