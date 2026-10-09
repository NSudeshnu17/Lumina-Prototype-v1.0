"""Salesperson routes — dashboard, item handling, logout."""
from flask import Blueprint, request, jsonify
from database.db import get_db, dict_from_row, dicts_from_rows
from services.product_service import handle_item_scan, get_case_products
from services.log_service import get_activity_logs

sp_bp = Blueprint('salesperson', __name__)

@sp_bp.route('/api/salesperson/dashboard', methods=['GET'])
def dashboard():
    employee_id = request.args.get('employee_id')
    if not employee_id:
        return jsonify({"error": "employee_id required"}), 400

    db = get_db()
    try:
        emp = dict_from_row(db.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,)).fetchone())
        if not emp:
            return jsonify({"error": "Employee not found."}), 404

        assignment = dict_from_row(db.execute(
            "SELECT * FROM case_assignments WHERE employee_id=? AND status='ACTIVE'",
            (employee_id,)
        ).fetchone())
        if not assignment:
            return jsonify({"error": "No active case assignment."}), 404

        case_id = assignment['case_id']
        products = get_case_products(case_id)

        stats = {
            'total': len(products),
            'available': sum(1 for p in products if p['current_status'] == 'AVAILABLE'),
            'in_handling': sum(1 for p in products if p['current_status'] == 'IN_HANDLING'),
            'billing': sum(1 for p in products if p['current_status'] == 'BILLING'),
            'sold': sum(1 for p in products if p['current_status'] == 'SOLD'),
        }

        recent = get_activity_logs(limit=20, employee_id=employee_id)

        return jsonify({
            "employee": emp,
            "case_id": case_id,
            "assignment": assignment,
            "products": products,
            "stats": stats,
            "recent_activity": recent
        })
    finally:
        db.close()

@sp_bp.route('/api/salesperson/scan-item', methods=['POST'])
def scan_item():
    data = request.json
    rfid_uid = data.get('rfid_uid', '').strip()
    employee_id = data.get('employee_id', '').strip()
    case_id = data.get('case_id', '').strip()

    if not all([rfid_uid, employee_id, case_id]):
        return jsonify({"success": False, "error": "RFID, employee_id, and case_id are required."}), 400

    # Verify employee still has this case assigned
    db = get_db()
    try:
        assignment = db.execute(
            "SELECT id FROM case_assignments WHERE employee_id=? AND case_id=? AND status='ACTIVE'",
            (employee_id, case_id)
        ).fetchone()
        if not assignment:
            return jsonify({"success": False, "error": "You are not currently assigned to this case."}), 403
    finally:
        db.close()

    result, error = handle_item_scan(rfid_uid, employee_id, case_id)
    if error:
        if isinstance(error, dict):
            return jsonify({"success": False, **error}), 409
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, **result})
