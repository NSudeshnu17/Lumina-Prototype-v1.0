"""Product service — product registration, state machine, handling."""
from database.db import get_db, dict_from_row, dicts_from_rows
from datetime import datetime

VALID_TRANSITIONS = {
    'AVAILABLE': ['IN_HANDLING'],
    'IN_HANDLING': ['AVAILABLE', 'BILLING'],
    'BILLING': ['IN_HANDLING', 'SOLD'],
    'SOLD': [],
}

def validate_transition(old_state, new_state):
    """Check if state transition is valid."""
    if old_state is None and new_state == 'AVAILABLE':
        return True
    allowed = VALID_TRANSITIONS.get(old_state, [])
    return new_state in allowed

def register_product(product_id, product_name, category, weight, price, case_id, rfid_uid):
    """Register a new product with RFID tag. Returns (product, error)."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check duplicate product_id
        if db.execute("SELECT id FROM products WHERE product_id=?", (product_id,)).fetchone():
            return None, f"Product ID '{product_id}' already exists."

        # Check case is functional
        case = dict_from_row(db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone())
        if not case:
            return None, f"Case '{case_id}' not found."
        if not case['functional']:
            return None, f"Case '{case_id}' is not functional."

        # Check RFID
        rfid_info = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())

        if rfid_info:
            if rfid_info['rfid_type'] == 'EMPLOYEE':
                emp = dict_from_row(db.execute("SELECT employee_id, name FROM employees WHERE rfid_uid=?", (rfid_uid,)).fetchone())
                return None, {"code": "EMPLOYEE_RFID", "message": "This RFID is registered as an Employee Card.",
                              "employee": emp}

            if rfid_info['status'] == 'ASSIGNED':
                active = dict_from_row(db.execute(
                    "SELECT ta.product_id, p.product_name, p.current_status, p.case_id FROM tag_assignments ta "
                    "JOIN products p ON ta.product_id = p.product_id "
                    "WHERE ta.rfid_uid=? AND ta.status='ACTIVE'", (rfid_uid,)
                ).fetchone())
                if active:
                    return None, {"code": "RFID_ASSIGNED", "message": "RFID already assigned to an active product.",
                                  "product": active}

            if rfid_info['status'] == 'RELEASED':
                # Tag previously used, available for reuse
                prev = dicts_from_rows(db.execute(
                    "SELECT ta.*, p.product_name, p.current_status FROM tag_assignments ta "
                    "JOIN products p ON ta.product_id = p.product_id "
                    "WHERE ta.rfid_uid=? ORDER BY ta.released_at DESC", (rfid_uid,)
                ).fetchall())
                return None, {"code": "RFID_RELEASED", "message": "RFID available for reuse.",
                              "previous_assignments": prev, "needs_confirmation": True}

        # All checks passed — create product
        db.execute(
            "INSERT INTO products (product_id, product_name, category, weight, price, case_id, current_status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (product_id, product_name, category, weight, price, case_id, 'AVAILABLE', now, now)
        )

        # Register RFID if new
        if not rfid_info:
            db.execute(
                "INSERT INTO rfid_registry (uid, rfid_type, status, created_at, updated_at) VALUES (?,?,?,?,?)",
                (rfid_uid, 'ITEM_TAG', 'ASSIGNED', now, now)
            )
        else:
            db.execute("UPDATE rfid_registry SET status='ASSIGNED', updated_at=? WHERE uid=?", (now, rfid_uid))

        # Create tag assignment
        db.execute(
            "INSERT INTO tag_assignments (rfid_uid, product_id, assigned_at, status) VALUES (?,?,?,?)",
            (rfid_uid, product_id, now, 'ACTIVE')
        )

        # State history
        db.execute(
            "INSERT INTO product_state_history (product_id, old_state, new_state, timestamp, reason) VALUES (?,?,?,?,?)",
            (product_id, None, 'AVAILABLE', now, 'Product registered')
        )

        # Activity log
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, case_id, details) VALUES (?,?,?,?,?,?,?)",
            (now, 'ADMIN', 'PRODUCT_REGISTERED', product_id, rfid_uid, case_id,
             f'{product_name} registered in {case_id}')
        )
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?)",
            (now, 'ADMIN', 'RFID_ASSIGNED', product_id, rfid_uid,
             f'Tag {rfid_uid} assigned to {product_id}')
        )

        db.commit()
        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone())
        return product, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def reassign_tag(rfid_uid, product_id, product_name, category, weight, price, case_id):
    """Reassign a released RFID tag to a new product."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Verify RFID is released
        rfid = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())
        if not rfid or rfid['status'] != 'RELEASED':
            return None, "RFID is not in RELEASED state."

        # Check duplicate product_id
        if db.execute("SELECT id FROM products WHERE product_id=?", (product_id,)).fetchone():
            return None, f"Product ID '{product_id}' already exists."

        # Create product
        db.execute(
            "INSERT INTO products (product_id, product_name, category, weight, price, case_id, current_status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (product_id, product_name, category, weight, price, case_id, 'AVAILABLE', now, now)
        )

        # Update RFID status
        db.execute("UPDATE rfid_registry SET status='ASSIGNED', updated_at=? WHERE uid=?", (now, rfid_uid))

        # New tag assignment (old ones preserved)
        db.execute(
            "INSERT INTO tag_assignments (rfid_uid, product_id, assigned_at, status) VALUES (?,?,?,?)",
            (rfid_uid, product_id, now, 'ACTIVE')
        )

        # State history
        db.execute(
            "INSERT INTO product_state_history (product_id, old_state, new_state, timestamp, reason) VALUES (?,?,?,?,?)",
            (product_id, None, 'AVAILABLE', now, 'Product registered via tag reassignment')
        )

        # Activity logs
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, case_id, details) VALUES (?,?,?,?,?,?,?)",
            (now, 'ADMIN', 'PRODUCT_REGISTERED', product_id, rfid_uid, case_id,
             f'{product_name} registered in {case_id}')
        )
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?)",
            (now, 'ADMIN', 'RFID_REASSIGNED', product_id, rfid_uid,
             f'Tag {rfid_uid} reassigned to {product_id} (previously used)')
        )

        db.commit()
        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone())
        return product, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def handle_item_scan(rfid_uid, employee_id, case_id):
    """Handle item RFID scan — remove or return. Returns (result, error)."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Find RFID
        rfid = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())
        if not rfid:
            return None, "Unknown RFID tag."
        if rfid['rfid_type'] != 'ITEM_TAG':
            return None, "This RFID is not a product tag."

        # Find active tag assignment
        tag = dict_from_row(db.execute(
            "SELECT * FROM tag_assignments WHERE rfid_uid=? AND status='ACTIVE'", (rfid_uid,)
        ).fetchone())
        if not tag:
            return None, "No active product assigned to this RFID."

        product = dict_from_row(db.execute(
            "SELECT * FROM products WHERE product_id=?", (tag['product_id'],)
        ).fetchone())
        if not product:
            return None, "Product not found."

        # Check case ownership
        if product['case_id'] != case_id:
            return None, {
                "code": "WRONG_CASE",
                "message": "Item does not belong to your case.",
                "product_id": product['product_id'],
                "product_case": product['case_id'],
                "your_case": case_id
            }

        status = product['current_status']

        if status == 'AVAILABLE':
            # Remove: AVAILABLE → IN_HANDLING
            db.execute(
                "UPDATE products SET current_status='IN_HANDLING', current_handler_employee_id=?, updated_at=? WHERE product_id=?",
                (employee_id, now, product['product_id'])
            )
            db.execute(
                "INSERT INTO product_state_history (product_id, old_state, new_state, employee_id, case_id, timestamp, reason) VALUES (?,?,?,?,?,?,?)",
                (product['product_id'], 'AVAILABLE', 'IN_HANDLING', employee_id, case_id, now, 'Item removed by salesperson')
            )
            db.execute(
                "INSERT INTO activity_logs (timestamp, employee_id, role, action, case_id, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?,?,?)",
                (now, employee_id, 'SALESPERSON', 'ITEM_REMOVED', case_id, product['product_id'], rfid_uid,
                 f'{product["product_name"]} removed from {case_id}')
            )
            db.commit()
            return {"action": "ITEM_REMOVED", "product": product['product_id'], "product_name": product['product_name'],
                    "old_state": "AVAILABLE", "new_state": "IN_HANDLING"}, None

        elif status == 'IN_HANDLING':
            # Check handler
            if product['current_handler_employee_id'] != employee_id:
                handler = dict_from_row(db.execute(
                    "SELECT name FROM employees WHERE employee_id=?", (product['current_handler_employee_id'],)
                ).fetchone())
                return None, {
                    "code": "HANDLED_BY_OTHER",
                    "message": "Item already in handling by another employee.",
                    "product_id": product['product_id'],
                    "handler": product['current_handler_employee_id'],
                    "handler_name": handler['name'] if handler else 'Unknown'
                }

            # Return: IN_HANDLING → AVAILABLE
            db.execute(
                "UPDATE products SET current_status='AVAILABLE', current_handler_employee_id=NULL, updated_at=? WHERE product_id=?",
                (now, product['product_id'])
            )
            db.execute(
                "INSERT INTO product_state_history (product_id, old_state, new_state, employee_id, case_id, timestamp, reason) VALUES (?,?,?,?,?,?,?)",
                (product['product_id'], 'IN_HANDLING', 'AVAILABLE', employee_id, case_id, now, 'Item returned by salesperson')
            )
            db.execute(
                "INSERT INTO activity_logs (timestamp, employee_id, role, action, case_id, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?,?,?)",
                (now, employee_id, 'SALESPERSON', 'ITEM_RETURNED', case_id, product['product_id'], rfid_uid,
                 f'{product["product_name"]} returned to {case_id}')
            )
            db.commit()
            return {"action": "ITEM_RETURNED", "product": product['product_id'], "product_name": product['product_name'],
                    "old_state": "IN_HANDLING", "new_state": "AVAILABLE"}, None

        elif status == 'BILLING':
            return None, f"Item {product['product_id']} is currently in BILLING. Cannot handle."
        elif status == 'SOLD':
            return None, f"Item {product['product_id']} is already SOLD."
        else:
            return None, f"Unknown product state: {status}"

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_case_products(case_id):
    """Get all products for a case."""
    db = get_db()
    try:
        products = dicts_from_rows(db.execute(
            "SELECT p.*, ta.rfid_uid FROM products p "
            "LEFT JOIN tag_assignments ta ON p.product_id = ta.product_id AND ta.status='ACTIVE' "
            "WHERE p.case_id=? ORDER BY p.product_id", (case_id,)
        ).fetchall())
        return products
    finally:
        db.close()

def get_product_state_history():
    """Get full product state history."""
    db = get_db()
    try:
        return dicts_from_rows(db.execute(
            "SELECT psh.*, p.product_name FROM product_state_history psh "
            "LEFT JOIN products p ON psh.product_id = p.product_id "
            "ORDER BY psh.timestamp DESC"
        ).fetchall())
    finally:
        db.close()
