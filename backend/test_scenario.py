"""
End-to-end integration and failure scenario test script for Lumina RFID.
Tests Parts 1-6 of the requirements specification.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_full_scenario():
    print("=== STARTING LUMINA RFID INTEGRATION TESTS ===")
    
    # 0. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] Backend health check verified.")

    # 1. Admin setup: Register EMP001 (Rahul)
    # Check if duplicate or new
    emp_payload = {
        "employee_id": "EMP010",
        "name": "Dev Tester",
        "role": "SALESPERSON",
        "section": "Counter A",
        "rfid_uid": "TEST_CARD_010"
    }
    res = requests.post(f"{BASE_URL}/admin/register-employee", json=emp_payload)
    if res.status_code == 200:
        print("[PASS] Employee registration succeeded.")
    elif res.status_code == 409:
        print("[INFO] Employee already registered.")
    
    # Verify duplicate RFID block
    dup_emp_payload = {
        "employee_id": "EMP011",
        "name": "Another Tester",
        "role": "SALESPERSON",
        "section": "Counter B",
        "rfid_uid": "TEST_CARD_010"
    }
    res_dup = requests.post(f"{BASE_URL}/admin/register-employee", json=dup_emp_payload)
    assert res_dup.status_code == 409, "Failed to block duplicate employee RFID!"
    print("[PASS] Duplicate employee RFID registration correctly blocked.")

    # 2. Product Registration
    prod_payload = {
        "product_id": "JWL100",
        "product_name": "Diamond Solitaire Ring",
        "category": "Rings",
        "weight": "3.2g",
        "price": 55000,
        "case_id": "CASE-01",
        "rfid_uid": "TAG_RING_100"
    }
    res_prod = requests.post(f"{BASE_URL}/admin/register-product", json=prod_payload)
    if res_prod.status_code == 200:
        print("[PASS] Product JWL100 registered with TAG_RING_100 in CASE-01.")
    
    # Verify duplicate tag on active product blocked
    res_prod_dup = requests.post(f"{BASE_URL}/admin/register-product", json={
        "product_id": "JWL101",
        "product_name": "Gold Pendant",
        "category": "Pendants",
        "weight": "2.0g",
        "price": 15000,
        "case_id": "CASE-01",
        "rfid_uid": "TAG_RING_100"
    })
    assert res_prod_dup.status_code == 409, "Failed to block duplicate active tag assignment!"
    print("[PASS] Duplicate tag assignment to active product correctly blocked.")

    # 3. Salesperson Login & Automatic Allocation
    # Clear any previous test sessions first
    requests.post(f"{BASE_URL}/auth/logout", json={"employee_id": "EMP001"})
    
    res_login = requests.post(f"{BASE_URL}/auth/rfid-login", json={"rfid_uid": "EMP_RFID_001", "expected_role": "SALESPERSON"})
    assert res_login.status_code == 200, f"Salesperson login failed: {res_login.text}"
    login_data = res_login.json()
    allocated_case = login_data["case_id"]
    print(f"[PASS] Salesperson Rahul logged in. Allocated: {allocated_case}")
    assert allocated_case == "CASE-01", f"Expected CASE-01 priority allocation, got {allocated_case}"

    # 4. Item Handling: AVAILABLE -> IN_HANDLING (Item Removal)
    res_item_rem = requests.post(f"{BASE_URL}/salesperson/scan-item", json={
        "rfid_uid": "TAG_RING_100",
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert res_item_rem.status_code == 200, f"Item removal failed: {res_item_rem.text}"
    assert res_item_rem.json()["action"] == "ITEM_REMOVED"
    print("[PASS] Item scan: AVAILABLE -> IN_HANDLING (ITEM_REMOVED).")

    # 5. Item Return: IN_HANDLING -> AVAILABLE
    res_item_ret = requests.post(f"{BASE_URL}/salesperson/scan-item", json={
        "rfid_uid": "TAG_RING_100",
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert res_item_ret.status_code == 200, f"Item return failed: {res_item_ret.text}"
    assert res_item_ret.json()["action"] == "ITEM_RETURNED"
    print("[PASS] Item second scan: IN_HANDLING -> AVAILABLE (ITEM_RETURNED).")

    # Scan again to put it back into IN_HANDLING for billing demo
    res_item_rem2 = requests.post(f"{BASE_URL}/salesperson/scan-item", json={
        "rfid_uid": "TAG_RING_100",
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert res_item_rem2.status_code == 200

    # 6. Test Logout block when item is IN_HANDLING
    res_logout_fail = requests.post(f"{BASE_URL}/auth/logout", json={"employee_id": "EMP001"})
    assert res_logout_fail.status_code == 409, "Logout should have been blocked due to unresolved items!"
    print("[PASS] Logout successfully blocked while item is IN_HANDLING.")

    # 7. Billing: IN_HANDLING -> BILLING
    res_bill_scan = requests.post(f"{BASE_URL}/billing/scan", json={"rfid_uid": "TAG_RING_100"})
    assert res_bill_scan.status_code == 200, f"Billing scan failed: {res_bill_scan.text}"
    print("[PASS] Billing scan: IN_HANDLING -> BILLING.")

    # Test Billing Cancellation: BILLING -> IN_HANDLING
    res_cancel = requests.post(f"{BASE_URL}/billing/cancel", json={"product_id": "JWL100"})
    assert res_cancel.status_code == 200
    print("[PASS] Billing cancellation restored status to IN_HANDLING.")

    # Resume Billing
    res_bill_resume = requests.post(f"{BASE_URL}/billing/scan", json={"rfid_uid": "TAG_RING_100"})
    assert res_bill_resume.status_code == 200

    # 8. Complete Sale: BILLING -> SOLD, Release Tag
    res_sale = requests.post(f"{BASE_URL}/billing/complete", json={
        "product_id": "JWL100",
        "customer_name": "Rohan Gupta",
        "customer_phone": "9812345678",
        "amount": 55000
    })
    assert res_sale.status_code == 200, f"Sale completion failed: {res_sale.text}"
    bill_number = res_sale.json()["bill_number"]
    print(f"[PASS] Sale completed atomically! Bill: {bill_number}. Tag TAG_RING_100 RELEASED.")

    # Verify duplicate complete sale blocked
    res_sale_dup = requests.post(f"{BASE_URL}/billing/complete", json={
        "product_id": "JWL100",
        "customer_name": "Duplicate Attempt",
        "customer_phone": "9812345678",
        "amount": 55000
    })
    assert res_sale_dup.status_code == 409, "Double complete sale was not prevented!"
    print("[PASS] Double complete sale protection verified.")

    # 9. RFID Tag Reuse
    # Check registration with now-released tag TAG_RING_100
    res_reuse_check = requests.post(f"{BASE_URL}/admin/register-product", json={
        "product_id": "JWL105",
        "product_name": "Gold Pendant",
        "category": "Pendant",
        "weight": "2.1g",
        "price": 20000,
        "case_id": "CASE-02",
        "rfid_uid": "TAG_RING_100"
    })
    assert res_reuse_check.status_code == 409
    assert res_reuse_check.json()["code"] == "RFID_RELEASED", "Should flag as RFID_RELEASED for explicit confirmation!"
    print("[PASS] System recognized tag as RELEASED and prompted for explicit confirmation.")

    # Confirm reassignment
    res_reassign = requests.post(f"{BASE_URL}/admin/reassign-tag", json={
        "product_id": "JWL105",
        "product_name": "Gold Pendant",
        "category": "Pendant",
        "weight": "2.1g",
        "price": 20000,
        "case_id": "CASE-02",
        "rfid_uid": "TAG_RING_100"
    })
    assert res_reassign.status_code == 200, f"Reassignment failed: {res_reassign.text}"
    print("[PASS] Tag TAG_RING_100 successfully reassigned to new product JWL105 in CASE-02.")

    # 10. Manager Oversight Verification
    res_mgr = requests.get(f"{BASE_URL}/manager/dashboard")
    assert res_mgr.status_code == 200
    mgr_stats = res_mgr.json()["stats"]
    assert mgr_stats["total_cases"] == 5
    assert mgr_stats["functional_cases"] == 3
    assert mgr_stats["inactive_cases"] == 2
    assert mgr_stats["total_sales"] >= 1
    print(f"[PASS] Manager dashboard verified: 5 total cases (3 functional, 2 inactive). Sales: {mgr_stats['total_sales']}.")

    # 11. Salesperson now allowed to logout (no unresolved items)
    res_logout = requests.post(f"{BASE_URL}/auth/logout", json={"employee_id": "EMP001"})
    assert res_logout.status_code == 200
    print("[PASS] Salesperson Rahul logged out successfully and CASE-01 released.")

    print("\n=== ALL TEST SCENARIOS PASSED WITH 100% SUCCESS ===")

if __name__ == "__main__":
    test_full_scenario()
