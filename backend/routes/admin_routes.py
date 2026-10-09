"""Admin routes — employee registration, product registration, case management."""
from flask import Blueprint, request, jsonify
from database.db import get_db, dict_from_row, dicts_from_rows
from services.product_service import register_product, reassign_tag
from services.rfid_service import get_rfid_info, get_all_rfids
from services.case_service import get_all_cases
from services.log_service import get_activity_logs
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/employees', methods=['GET'])
def list_employees():
    db = get_db()
    try:
        rows = dicts_from_rows(db.execute("SELECT * FROM employees ORDER BY employee_id").fetchall())
        return jsonify(rows)
    finally:
        db.close()

@admin_bp.route('/api/admin/register-employee', methods=['POST'])
def register_employee():
    data = request.json
    employee_id = data.get('employee_id', '').strip()
    name = data.get('name', '').strip()
    role = data.get('role', '').strip()
    section = data.get('section', '').strip()
    rfid_uid = data.get('rfid_uid', '').strip()

    if not all([employee_id, name, role]):
        return jsonify({"success": False, "error": "Employee ID, Name, and Role are required."}), 400
    if role not in ('ADMIN', 'MANAGER', 'SALESPERSON'):
        return jsonify({"success": False, "error": "Invalid role."}), 400

    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check duplicate employee ID
        if db.execute("SELECT id FROM employees WHERE employee_id=?", (employee_id,)).fetchone():
            return jsonify({"success": False, "error": f"Employee ID '{employee_id}' already exists."}), 409

        # Check RFID if provided
        if rfid_uid:
            rfid = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())
            if rfid:
                if rfid['rfid_type'] == 'ITEM_TAG':
                    return jsonify({"success": False, "error": "This RFID is registered as a Product Tag. Cannot use for employee.",
                                    "code": "ITEM_TAG_RFID"}), 409
                if rfid['rfid_type'] == 'EMPLOYEE':
                    emp = dict_from_row(db.execute("SELECT employee_id, name FROM employees WHERE rfid_uid=?", (rfid_uid,)).fetchone())
                    return jsonify({"success": False, "error": "RFID already registered as an Employee Card.",
                                    "code": "DUPLICATE_EMPLOYEE_RFID", "existing_employee": emp}), 409

            # Check if another employee has this RFID
            existing = db.execute("SELECT employee_id, name FROM employees WHERE rfid_uid=?", (rfid_uid,)).fetchone()
            if existing:
                return jsonify({"success": False, "error": "RFID already assigned to another employee.",
                                "existing_employee": dict(existing)}), 409

        # Create employee
        db.execute(
            "INSERT INTO employees (employee_id, name, role, section, rfid_uid, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (employee_id, name, role, section, rfid_uid or None, now, now)
        )

        # Register RFID
        if rfid_uid:
            existing_rfid = db.execute("SELECT id FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone()
            if not existing_rfid:
                db.execute(
                    "INSERT INTO rfid_registry (uid, rfid_type, status, created_at, updated_at) VALUES (?,?,?,?,?)",
                    (rfid_uid, 'EMPLOYEE', 'ACTIVE', now, now)
                )

        # Activity log
        db.execute(
            "INSERT INTO activity_logs (timestamp, employee_id, role, action, rfid_uid, details) VALUES (?,?,?,?,?,?)",
            (now, employee_id, role, 'EMPLOYEE_REGISTERED', rfid_uid, f'{name} ({role}) registered')
        )

        db.commit()
        emp = dict_from_row(db.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,)).fetchone())
        return jsonify({"success": True, "employee": emp})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@admin_bp.route('/api/admin/register-product', methods=['POST'])
def admin_register_product():
    data = request.json
    product_id = data.get('product_id', '').strip()
    product_name = data.get('product_name', '').strip()
    category = data.get('category', '').strip()
    weight = data.get('weight', '').strip()
    price = data.get('price', 0)
    case_id = data.get('case_id', '').strip()
    rfid_uid = data.get('rfid_uid', '').strip()

    if not all([product_id, product_name, case_id, rfid_uid]):
        return jsonify({"success": False, "error": "Product ID, Name, Case, and RFID are required."}), 400

    try:
        price = float(price) if price else 0
    except (ValueError, TypeError):
        price = 0

    product, error = register_product(product_id, product_name, category, weight, price, case_id, rfid_uid)
    if error:
        if isinstance(error, dict):
            return jsonify({"success": False, **error}), 409
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, "product": product})

@admin_bp.route('/api/admin/reassign-tag', methods=['POST'])
def admin_reassign_tag():
    data = request.json
    rfid_uid = data.get('rfid_uid', '').strip()
    product_id = data.get('product_id', '').strip()
    product_name = data.get('product_name', '').strip()
    category = data.get('category', '').strip()
    weight = data.get('weight', '').strip()
    price = data.get('price', 0)
    case_id = data.get('case_id', '').strip()

    if not all([rfid_uid, product_id, product_name, case_id]):
        return jsonify({"success": False, "error": "RFID, Product ID, Name, and Case are required."}), 400

    try:
        price = float(price) if price else 0
    except (ValueError, TypeError):
        price = 0

    product, error = reassign_tag(rfid_uid, product_id, product_name, category, weight, price, case_id)
    if error:
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, "product": product})

@admin_bp.route('/api/admin/cases', methods=['GET'])
def list_cases():
    return jsonify(get_all_cases())

@admin_bp.route('/api/admin/rfid-registry', methods=['GET'])
def list_rfids():
    return jsonify(get_all_rfids())

@admin_bp.route('/api/admin/rfid-check', methods=['POST'])
def check_rfid():
    """Check what an RFID UID is associated with."""
    data = request.json
    uid = data.get('rfid_uid', '').strip()
    if not uid:
        return jsonify({"error": "RFID UID required."}), 400
    info = get_rfid_info(uid)
    if not info:
        return jsonify({"found": False, "uid": uid})
    return jsonify({"found": True, **info})

@admin_bp.route('/api/admin/activity-logs', methods=['GET'])
def list_activity_logs():
    limit = request.args.get('limit', 100, type=int)
    action = request.args.get('action')
    employee_id = request.args.get('employee_id')
    return jsonify(get_activity_logs(limit, action, employee_id))

@admin_bp.route('/api/admin/products', methods=['GET'])
def list_all_products():
    db = get_db()
    try:
        products = dicts_from_rows(db.execute(
            "SELECT p.*, ta.rfid_uid FROM products p "
            "LEFT JOIN tag_assignments ta ON p.product_id = ta.product_id AND ta.status='ACTIVE' "
            "ORDER BY p.product_id"
        ).fetchall())
        return jsonify(products)
    finally:
        db.close()
