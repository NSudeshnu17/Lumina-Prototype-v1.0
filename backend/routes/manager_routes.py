"""Manager routes — dashboard, history views."""
from flask import Blueprint, request, jsonify
from database.db import get_db, dicts_from_rows
from services.log_service import get_dashboard_stats, get_activity_logs
from services.case_service import get_all_cases, get_case_assignment_history
from services.product_service import get_product_state_history
from services.billing_service import get_sales_history
from services.rfid_service import get_all_rfids

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/api/manager/dashboard', methods=['GET'])
def dashboard():
    stats = get_dashboard_stats()
    cases = get_all_cases()
    return jsonify({"stats": stats, "cases": cases})

@manager_bp.route('/api/manager/activity-logs', methods=['GET'])
def activity_logs():
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_activity_logs(limit))

@manager_bp.route('/api/manager/case-history', methods=['GET'])
def case_history():
    return jsonify(get_case_assignment_history())

@manager_bp.route('/api/manager/product-history', methods=['GET'])
def product_history():
    return jsonify(get_product_state_history())

@manager_bp.route('/api/manager/sales', methods=['GET'])
def sales():
    return jsonify(get_sales_history())

@manager_bp.route('/api/manager/rfid-history', methods=['GET'])
def rfid_history():
    return jsonify(get_all_rfids())

@manager_bp.route('/api/manager/products', methods=['GET'])
def all_products():
    db = get_db()
    try:
        return jsonify(dicts_from_rows(db.execute(
            "SELECT p.*, ta.rfid_uid FROM products p "
            "LEFT JOIN tag_assignments ta ON p.product_id = ta.product_id AND ta.status='ACTIVE' "
            "ORDER BY p.product_id"
        ).fetchall()))
    finally:
        db.close()
