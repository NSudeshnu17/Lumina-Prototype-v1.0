"""Billing routes — scan for billing, cancel, complete sale."""
from flask import Blueprint, request, jsonify
from services.billing_service import scan_for_billing, cancel_billing, complete_sale, get_sales_history

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/api/billing/scan', methods=['POST'])
def billing_scan():
    data = request.json
    rfid_uid = data.get('rfid_uid', '').strip()
    if not rfid_uid:
        return jsonify({"success": False, "error": "RFID UID required."}), 400

    product, error = scan_for_billing(rfid_uid)
    if error:
        if isinstance(error, dict):
            return jsonify({"success": False, **error}), 409
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, "product": product})

@billing_bp.route('/api/billing/cancel', methods=['POST'])
def billing_cancel():
    data = request.json
    product_id = data.get('product_id', '').strip()
    if not product_id:
        return jsonify({"success": False, "error": "Product ID required."}), 400

    result, error = cancel_billing(product_id)
    if error:
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, **result})

@billing_bp.route('/api/billing/complete', methods=['POST'])
def billing_complete():
    data = request.json
    product_id = data.get('product_id', '').strip()
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    amount = data.get('amount', 0)

    if not product_id:
        return jsonify({"success": False, "error": "Product ID required."}), 400

    try:
        amount = float(amount) if amount else 0
    except (ValueError, TypeError):
        amount = 0

    result, error = complete_sale(product_id, customer_name, customer_phone, amount)
    if error:
        return jsonify({"success": False, "error": error}), 409
    return jsonify({"success": True, **result})

@billing_bp.route('/api/billing/sales', methods=['GET'])
def list_sales():
    return jsonify(get_sales_history())
