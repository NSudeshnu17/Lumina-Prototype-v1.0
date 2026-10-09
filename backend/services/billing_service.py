"""Billing service — handles billing lifecycle and sale completion."""
from database.db import get_db, dict_from_row, dicts_from_rows
from datetime import datetime

def scan_for_billing(rfid_uid):
    """Scan a product RFID for billing. Returns (product_info, error)."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        rfid = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())
        if not rfid:
            return None, "Unknown RFID tag."
        if rfid['rfid_type'] != 'ITEM_TAG':
            return None, "This RFID is not a product tag."

        tag = dict_from_row(db.execute(
            "SELECT * FROM tag_assignments WHERE rfid_uid=? AND status='ACTIVE'", (rfid_uid,)
        ).fetchone())
        if not tag:
            return None, "No active product assigned to this RFID."

        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (tag['product_id'],)).fetchone())
        if not product:
            return None, "Product not found."

        if product['current_status'] == 'SOLD':
            sale = dict_from_row(db.execute(
                "SELECT * FROM sales WHERE product_id=?", (product['product_id'],)
            ).fetchone())
            return None, {"code": "ALREADY_SOLD", "message": "Item already sold.",
                          "product": product, "sale": sale}

        if product['current_status'] == 'AVAILABLE':
            return None, "Item is AVAILABLE. It must be IN_HANDLING before billing."

        if product['current_status'] == 'BILLING':
            return None, "Item is already in BILLING state."

        if product['current_status'] != 'IN_HANDLING':
            return None, f"Item is in {product['current_status']} state. Cannot bill."

        # IN_HANDLING → BILLING
        db.execute(
            "UPDATE products SET current_status='BILLING', updated_at=? WHERE product_id=?",
            (now, product['product_id'])
        )
        db.execute(
            "INSERT INTO product_state_history (product_id, old_state, new_state, timestamp, reason) VALUES (?,?,?,?,?)",
            (product['product_id'], 'IN_HANDLING', 'BILLING', now, 'Billing started by admin')
        )
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?)",
            (now, 'ADMIN', 'BILLING_STARTED', product['product_id'], rfid_uid,
             f'Billing started for {product["product_name"]}')
        )
        db.commit()

        # Re-fetch updated product
        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (tag['product_id'],)).fetchone())
        handler = None
        if product['current_handler_employee_id']:
            handler = dict_from_row(db.execute(
                "SELECT employee_id, name FROM employees WHERE employee_id=?",
                (product['current_handler_employee_id'],)
            ).fetchone())
        product['handler'] = handler
        return product, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def cancel_billing(product_id):
    """Cancel billing: BILLING → IN_HANDLING."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone())
        if not product:
            return None, "Product not found."
        if product['current_status'] != 'BILLING':
            return None, f"Product is not in BILLING state (current: {product['current_status']})."

        db.execute(
            "UPDATE products SET current_status='IN_HANDLING', updated_at=? WHERE product_id=?",
            (now, product_id)
        )
        db.execute(
            "INSERT INTO product_state_history (product_id, old_state, new_state, timestamp, reason) VALUES (?,?,?,?,?)",
            (product_id, 'BILLING', 'IN_HANDLING', now, 'Billing cancelled')
        )
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, details) VALUES (?,?,?,?,?)",
            (now, 'ADMIN', 'BILLING_CANCELLED', product_id, f'Billing cancelled for {product["product_name"]}')
        )
        db.commit()
        return {"product_id": product_id, "new_state": "IN_HANDLING"}, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def complete_sale(product_id, customer_name, customer_phone, amount):
    """Complete sale: BILLING → SOLD, release RFID tag, create sale record."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        product = dict_from_row(db.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone())
        if not product:
            return None, "Product not found."
        if product['current_status'] != 'BILLING':
            return None, f"Product is not in BILLING state (current: {product['current_status']})."

        # Check if already sold (double-click protection)
        existing_sale = db.execute("SELECT id FROM sales WHERE product_id=?", (product_id,)).fetchone()
        if existing_sale:
            return None, "Sale already completed for this product."

        # Generate bill number
        last_bill = db.execute("SELECT bill_number FROM sales ORDER BY id DESC LIMIT 1").fetchone()
        if last_bill:
            num = int(last_bill[0].split('-')[1]) + 1
        else:
            num = 1
        bill_number = f"BILL-{num:04d}"

        # BILLING → SOLD
        db.execute(
            "UPDATE products SET current_status='SOLD', current_handler_employee_id=NULL, sold_at=?, updated_at=? WHERE product_id=?",
            (now, now, product_id)
        )

        # Create sale record
        db.execute(
            "INSERT INTO sales (bill_number, product_id, employee_id, customer_name, customer_phone, amount, created_at) VALUES (?,?,?,?,?,?,?)",
            (bill_number, product_id, product['current_handler_employee_id'], customer_name, customer_phone, amount or product['price'], now)
        )

        # Close tag assignment
        tag = dict_from_row(db.execute(
            "SELECT * FROM tag_assignments WHERE product_id=? AND status='ACTIVE'", (product_id,)
        ).fetchone())
        rfid_uid = None
        if tag:
            rfid_uid = tag['rfid_uid']
            db.execute(
                "UPDATE tag_assignments SET released_at=?, status='RELEASED' WHERE id=?",
                (now, tag['id'])
            )
            db.execute(
                "UPDATE rfid_registry SET status='RELEASED', updated_at=? WHERE uid=?",
                (now, rfid_uid)
            )

        # State history
        db.execute(
            "INSERT INTO product_state_history (product_id, old_state, new_state, timestamp, reason) VALUES (?,?,?,?,?)",
            (product_id, 'BILLING', 'SOLD', now, f'Sale completed - {bill_number}')
        )

        # Activity logs
        db.execute(
            "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?)",
            (now, 'ADMIN', 'SALE_COMPLETED', product_id, rfid_uid,
             f'{product["product_name"]} sold - {bill_number} - Customer: {customer_name}')
        )
        if rfid_uid:
            db.execute(
                "INSERT INTO activity_logs (timestamp, role, action, product_id, rfid_uid, details) VALUES (?,?,?,?,?,?)",
                (now, 'ADMIN', 'RFID_RELEASED', product_id, rfid_uid,
                 f'Tag {rfid_uid} released after sale of {product["product_name"]}')
            )

        db.commit()
        return {"bill_number": bill_number, "product_id": product_id, "amount": amount or product['price'],
                "customer_name": customer_name, "sold_at": now}, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_sales_history():
    """Get all sales."""
    db = get_db()
    try:
        return dicts_from_rows(db.execute(
            "SELECT s.*, p.product_name, p.category FROM sales s "
            "JOIN products p ON s.product_id = p.product_id "
            "ORDER BY s.created_at DESC"
        ).fetchall())
    finally:
        db.close()
