"""RFID service — central RFID registry operations."""
from database.db import get_db, dict_from_row, dicts_from_rows
from datetime import datetime

def get_rfid_info(uid):
    """Get full info about an RFID UID including its current assignment."""
    db = get_db()
    try:
        registry = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (uid,)).fetchone())
        if not registry:
            return None

        result = {**registry}

        if registry['rfid_type'] == 'EMPLOYEE':
            emp = dict_from_row(db.execute("SELECT * FROM employees WHERE rfid_uid=?", (uid,)).fetchone())
            result['employee'] = emp
        elif registry['rfid_type'] == 'ITEM_TAG':
            # Get current active assignment
            active = dict_from_row(db.execute(
                "SELECT ta.*, p.product_name, p.current_status, p.case_id FROM tag_assignments ta "
                "JOIN products p ON ta.product_id = p.product_id "
                "WHERE ta.rfid_uid=? AND ta.status='ACTIVE'", (uid,)
            ).fetchone())
            result['active_assignment'] = active

            # Get all historical assignments
            history = dicts_from_rows(db.execute(
                "SELECT ta.*, p.product_name, p.current_status FROM tag_assignments ta "
                "JOIN products p ON ta.product_id = p.product_id "
                "WHERE ta.rfid_uid=? ORDER BY ta.assigned_at DESC", (uid,)
            ).fetchall())
            result['assignment_history'] = history

        return result
    finally:
        db.close()

def register_rfid(uid, rfid_type):
    """Register a new RFID in the central registry."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            "INSERT INTO rfid_registry (uid, rfid_type, status, created_at, updated_at) VALUES (?,?,?,?,?)",
            (uid, rfid_type, 'ACTIVE' if rfid_type == 'EMPLOYEE' else 'ASSIGNED', now, now)
        )
        db.commit()
    finally:
        db.close()

def update_rfid_status(uid, status):
    """Update RFID status."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute("UPDATE rfid_registry SET status=?, updated_at=? WHERE uid=?", (status, now, uid))
        db.commit()
    finally:
        db.close()

def get_all_rfids():
    """Get all RFID registry entries with assignment details."""
    db = get_db()
    try:
        rfids = dicts_from_rows(db.execute("SELECT * FROM rfid_registry ORDER BY created_at DESC").fetchall())
        for r in rfids:
            if r['rfid_type'] == 'EMPLOYEE':
                emp = dict_from_row(db.execute("SELECT employee_id, name FROM employees WHERE rfid_uid=?", (r['uid'],)).fetchone())
                r['employee'] = emp
                r['current_assignment'] = emp['name'] if emp else None
            elif r['rfid_type'] == 'ITEM_TAG':
                active = dict_from_row(db.execute(
                    "SELECT ta.product_id, p.product_name, p.case_id FROM tag_assignments ta "
                    "JOIN products p ON ta.product_id = p.product_id "
                    "WHERE ta.rfid_uid=? AND ta.status='ACTIVE'", (r['uid'],)
                ).fetchone())
                r['active_product'] = active
                r['current_assignment'] = active['product_name'] if active else None

                history = dicts_from_rows(db.execute(
                    "SELECT ta.*, p.product_name, p.current_status FROM tag_assignments ta "
                    "JOIN products p ON ta.product_id = p.product_id "
                    "WHERE ta.rfid_uid=? ORDER BY ta.assigned_at DESC", (r['uid'],)
                ).fetchall())
                r['assignment_history'] = history
        return rfids
    finally:
        db.close()
