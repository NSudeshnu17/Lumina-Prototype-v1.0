"""Auth routes — admin login, salesperson/manager RFID login."""
from flask import Blueprint, request, jsonify, session
from database.db import get_db, dict_from_row
from services.case_service import allocate_case, release_case
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    password = data.get('password', '')
    if password == 'admin123':
        session['role'] = 'ADMIN'
        session['employee_id'] = 'ADM001'
        session['name'] = 'Admin User'
        return jsonify({"success": True, "employee_id": "ADM001", "name": "Admin User", "role": "ADMIN"})
    return jsonify({"success": False, "error": "Invalid password."}), 401

@auth_bp.route('/api/auth/rfid-login', methods=['POST'])
def rfid_login():
    """RFID-based login for salesperson or manager."""
    data = request.json
    rfid_uid = data.get('rfid_uid', '').strip()
    expected_role = data.get('expected_role', '')  # SALESPERSON or MANAGER

    if not rfid_uid:
        return jsonify({"success": False, "error": "RFID UID is required."}), 400

    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check RFID registry
        rfid = dict_from_row(db.execute("SELECT * FROM rfid_registry WHERE uid=?", (rfid_uid,)).fetchone())
        if not rfid:
            return jsonify({"success": False, "error": "Unknown RFID card."}), 404
        if rfid['rfid_type'] != 'EMPLOYEE':
            return jsonify({"success": False, "error": "This RFID is not an employee card."}), 400

        # Find employee
        emp = dict_from_row(db.execute("SELECT * FROM employees WHERE rfid_uid=?", (rfid_uid,)).fetchone())
        if not emp:
            return jsonify({"success": False, "error": "Employee not found for this RFID."}), 404
        if not emp['active']:
            return jsonify({"success": False, "error": "Employee account is inactive."}), 403
        if expected_role and emp['role'] != expected_role:
            return jsonify({"success": False, "error": f"Access denied. Expected {expected_role}, found {emp['role']}."}), 403

        result = {
            "success": True,
            "employee_id": emp['employee_id'],
            "name": emp['name'],
            "role": emp['role']
        }

        if emp['role'] == 'SALESPERSON':
            case_id, error = allocate_case(emp['employee_id'])
            if error:
                return jsonify({"success": False, "error": error}), 409
            result['case_id'] = case_id

        # Log login
        db.execute(
            "INSERT INTO activity_logs (timestamp, employee_id, role, action, details) VALUES (?,?,?,?,?)",
            (now, emp['employee_id'], emp['role'], 'LOGIN', f'{emp["name"]} logged in')
        )
        db.commit()

        session['role'] = emp['role']
        session['employee_id'] = emp['employee_id']
        session['name'] = emp['name']
        if emp['role'] == 'SALESPERSON':
            session['case_id'] = result.get('case_id')

        return jsonify(result)
    finally:
        db.close()

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    data = request.json or {}
    employee_id = data.get('employee_id', session.get('employee_id'))
    if not employee_id:
        session.clear()
        return jsonify({"success": True})

    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emp = dict_from_row(db.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,)).fetchone())

        if emp and emp['role'] == 'SALESPERSON':
            case_id, error = release_case(employee_id)
            if error:
                if isinstance(error, dict):
                    return jsonify({"success": False, **error}), 409
                return jsonify({"success": False, "error": error}), 409

        db.execute(
            "INSERT INTO activity_logs (timestamp, employee_id, role, action, details) VALUES (?,?,?,?,?)",
            (now, employee_id, emp['role'] if emp else 'UNKNOWN', 'LOGOUT', f'{emp["name"] if emp else employee_id} logged out')
        )
        db.commit()
    finally:
        db.close()

    session.clear()
    return jsonify({"success": True})

@auth_bp.route('/api/auth/session', methods=['GET'])
def get_session():
    if session.get('employee_id'):
        return jsonify({
            "logged_in": True,
            "employee_id": session['employee_id'],
            "name": session['name'],
            "role": session['role'],
            "case_id": session.get('case_id')
        })
    return jsonify({"logged_in": False})
