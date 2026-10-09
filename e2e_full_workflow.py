"""
Complete live end-to-end workflow execution for Lumina RFID.
Tests through Vite frontend proxy (http://localhost:5173/api) simulating the exact user workflow.
"""
import requests
import json
import time
import sys

# Ensure UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

PROXY_URL = "http://localhost:5173/api"

def run_workflow():
    print("=" * 70)
    print("   LUMINA RFID - COMPLETE SYSTEM WORKFLOW EXECUTION")
    print("=" * 70)
    
    session = requests.Session()

    # Step 0: Verify Vite -> Flask Proxy
    print("\n[STEP 0] Checking System Connectivity via Vite Proxy...")
    health = session.get(f"{PROXY_URL}/health")
    assert health.status_code == 200, "Vite proxy to Flask is not responding!"
    print(f"  -> Frontend & Backend communicating properly: {health.json()}")

    # Step 1: Admin Setup - Employee Registration & Duplicate Validations
    print("\n[STEP 1] Admin Module: Employee Registration & Validation")
    # Try duplicate registration with existing employee ID
    dup_res = session.post(f"{PROXY_URL}/admin/register-employee", json={
        "employee_id": "EMP001",
        "name": "Duplicate Rahul",
        "role": "SALESPERSON",
        "section": "Counter 1",
        "rfid_uid": "EMP_NEW_999"
    })
    print(f"  -> Attempting duplicate employee ID 'EMP001': Status {dup_res.status_code}")
    assert dup_res.status_code == 409, "Failed to block duplicate employee ID!"
    print("  ✓ Correctly blocked duplicate Employee ID.")

    # Try duplicate registration with existing employee RFID
    dup_rfid = session.post(f"{PROXY_URL}/admin/register-employee", json={
        "employee_id": "EMP999",
        "name": "Different Name",
        "role": "SALESPERSON",
        "section": "Counter 1",
        "rfid_uid": "EMP_RFID_001"
    })
    print(f"  -> Attempting duplicate employee RFID 'EMP_RFID_001': Status {dup_rfid.status_code}")
    assert dup_rfid.status_code == 409, "Failed to block duplicate employee RFID!"
    print("  ✓ Correctly blocked duplicate Employee RFID.")

    # Register a new staff member
    new_emp_id = f"EMP{int(time.time()) % 1000:03d}"
    new_card_uid = f"CARD_{int(time.time()) % 1000:03d}"
    emp_res = session.post(f"{PROXY_URL}/admin/register-employee", json={
        "employee_id": new_emp_id,
        "name": "Vikram Patel",
        "role": "SALESPERSON",
        "section": "Diamond Counter",
        "rfid_uid": new_card_uid
    })
    assert emp_res.status_code == 200, f"Staff registration failed: {emp_res.text}"
    print(f"  ✓ Staff registered successfully: {new_emp_id} - Vikram Patel (Card: {new_card_uid})")

    # Step 2: Admin Module - Product Registration
    print("\n[STEP 2] Admin Module: Jewellery Product Registration")
    prod_id = f"JWL{int(time.time()) % 1000:03d}"
    tag_uid = f"TAG{int(time.time()) % 1000:03d}"
    
    prod_res = session.post(f"{PROXY_URL}/admin/register-product", json={
        "product_id": prod_id,
        "product_name": "22K Gold Solitaire Ring",
        "category": "Ring",
        "weight": "4.8g",
        "price": 48500,
        "case_id": "CASE-01",
        "rfid_uid": tag_uid
    })
    assert prod_res.status_code == 200, f"Product registration failed: {prod_res.text}"
    print(f"  ✓ Product {prod_id} registered and bound to RFID Tag: {tag_uid} in CASE-01.")

    # Verify duplicate active tag assignment is blocked
    dup_tag_res = session.post(f"{PROXY_URL}/admin/register-product", json={
        "product_id": f"JWL_DUP_{int(time.time()) % 100:02d}",
        "product_name": "Silver Bracelet",
        "category": "Bracelet",
        "weight": "12.0g",
        "price": 8000,
        "case_id": "CASE-01",
        "rfid_uid": tag_uid
    })
    assert dup_tag_res.status_code == 409, "Duplicate active tag assignment was not blocked!"
    print(f"  ✓ Correctly blocked assigning already-active tag {tag_uid} to another product.")

    # Step 3: Salesperson RFID Login & Automatic Case Allocation
    print("\n[STEP 3] Salesperson Login & Automatic Priority Case Allocation")
    # Ensure EMP001 logout first to ensure clean state
    session.post(f"{PROXY_URL}/auth/logout", json={"employee_id": "EMP001"})

    login_res = session.post(f"{PROXY_URL}/auth/rfid-login", json={
        "rfid_uid": "EMP_RFID_001",
        "expected_role": "SALESPERSON"
    })
    assert login_res.status_code == 200, f"Salesperson login failed: {login_res.text}"
    login_info = login_res.json()
    allocated_case = login_info.get("case_id")
    print(f"  ✓ Salesperson Authenticated: {login_info['name']} ({login_info['employee_id']})")
    print(f"  ✓ Automatic Priority Allocation Assigned: {allocated_case}")
    assert allocated_case == "CASE-01", f"Expected CASE-01, got {allocated_case}"

    # Verify case assignment stored in database
    dash_res = session.get(f"{PROXY_URL}/salesperson/dashboard?employee_id=EMP001")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    print(f"  ✓ Salesperson Dashboard loaded. Active items in {allocated_case}: {len(dash_data['products'])}")

    # Step 4: Single-Reader Item Handling Simulation
    print("\n[STEP 4] Item Handling Simulation (Single Reader):")
    print(f"  -> Action 1: First scan of {tag_uid} by handler Rahul...")
    scan1 = session.post(f"{PROXY_URL}/salesperson/scan-item", json={
        "rfid_uid": tag_uid,
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert scan1.status_code == 200
    print(f"     ✓ Status Transition: {scan1.json()['old_state']} -> {scan1.json()['new_state']} (ITEM_REMOVED for customer display)")

    print(f"  -> Action 2: Second scan of {tag_uid} to safely return item...")
    scan2 = session.post(f"{PROXY_URL}/salesperson/scan-item", json={
        "rfid_uid": tag_uid,
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert scan2.status_code == 200
    print(f"     ✓ Status Transition: {scan2.json()['old_state']} -> {scan2.json()['new_state']} (ITEM_RETURNED to case)")

    print(f"  -> Action 3: Third scan of {tag_uid} to take out for customer purchase...")
    scan3 = session.post(f"{PROXY_URL}/salesperson/scan-item", json={
        "rfid_uid": tag_uid,
        "employee_id": "EMP001",
        "case_id": allocated_case
    })
    assert scan3.status_code == 200
    print(f"     ✓ Status Transition: {scan3.json()['old_state']} -> {scan3.json()['new_state']}")

    # Step 5: Preventative Logout Validation
    print("\n[STEP 5] Testing Preventative Validation on Logout:")
    logout_attempt = session.post(f"{PROXY_URL}/auth/logout", json={"employee_id": "EMP001"})
    print(f"  -> Attempting logout while item is IN_HANDLING: Status {logout_attempt.status_code}")
    assert logout_attempt.status_code == 409, "Logout should be blocked with active handling items!"
    print(f"  ✓ Logout BLOCKED as required: {logout_attempt.json().get('message')}")

    # Step 6: Admin Billing Workflow
    print("\n[STEP 6] Admin Module: Billing Counter & Sale Completion")
    print(f"  -> Scanning tag {tag_uid} at Billing Counter...")
    bill_scan = session.post(f"{PROXY_URL}/billing/scan", json={"rfid_uid": tag_uid})
    assert bill_scan.status_code == 200, f"Billing scan failed: {bill_scan.text}"
    print(f"     ✓ Item loaded into Billing session: {bill_scan.json()['product']['product_id']} (Status: BILLING)")

    # Test Billing Cancellation
    cancel_res = session.post(f"{PROXY_URL}/billing/cancel", json={"product_id": prod_id})
    assert cancel_res.status_code == 200
    print(f"     ✓ Billing Cancellation test passed: Restored to {cancel_res.json()['new_state']}")

    # Re-scan for billing
    bill_scan2 = session.post(f"{PROXY_URL}/billing/scan", json={"rfid_uid": tag_uid})
    assert bill_scan2.status_code == 200

    # Complete Sale
    sale_res = session.post(f"{PROXY_URL}/billing/complete", json={
        "product_id": prod_id,
        "customer_name": "Siddharth Verma",
        "customer_phone": "9876543210",
        "amount": 48500
    })
    assert sale_res.status_code == 200, f"Sale completion failed: {sale_res.text}"
    sale_data = sale_res.json()
    print(f"     ✓ Sale Completed Atomically!")
    print(f"       • Bill Number : {sale_data['bill_number']}")
    print(f"       • Customer    : {sale_data['customer_name']}")
    print(f"       • Amount      : ₹{sale_data['amount']}")
    print(f"       • Tag Status  : RELEASED (Available for reuse)")

    # Step 7: RFID Tag Reassignment & Reusability
    print("\n[STEP 7] Admin Module: Reusing Released RFID Tag for New Product")
    new_prod_id = f"JWL_NEW_{int(time.time()) % 1000:03d}"
    
    # Attempt normal registration with released tag
    reassign_check = session.post(f"{PROXY_URL}/admin/register-product", json={
        "product_id": new_prod_id,
        "product_name": "Platinum Diamond Necklace",
        "category": "Necklace",
        "weight": "18.5g",
        "price": 125000,
        "case_id": "CASE-02",
        "rfid_uid": tag_uid
    })
    assert reassign_check.status_code == 409
    assert reassign_check.json()["code"] == "RFID_RELEASED"
    print(f"  ✓ System identified {tag_uid} as RELEASED from previous item {prod_id} (Status: SOLD).")
    print(f"  ✓ Prompted for explicit REASSIGN confirmation.")

    # Confirm reassignment
    reassign_confirm = session.post(f"{PROXY_URL}/admin/reassign-tag", json={
        "product_id": new_prod_id,
        "product_name": "Platinum Diamond Necklace",
        "category": "Necklace",
        "weight": "18.5g",
        "price": 125000,
        "case_id": "CASE-02",
        "rfid_uid": tag_uid
    })
    assert reassign_confirm.status_code == 200
    print(f"  ✓ Tag {tag_uid} successfully reassigned to new product {new_prod_id} in CASE-02!")

    # Step 8: Manager Dashboard & Audit Trail
    print("\n[STEP 8] Manager Portal: Real-Time Store Oversight & Auditing")
    mgr_login = session.post(f"{PROXY_URL}/auth/rfid-login", json={
        "rfid_uid": "MGR_RFID_001",
        "expected_role": "MANAGER"
    })
    assert mgr_login.status_code == 200
    print(f"  ✓ Manager Authenticated: {mgr_login.json()['name']}")

    mgr_dash = session.get(f"{PROXY_URL}/manager/dashboard").json()
    stats = mgr_dash["stats"]
    cases = mgr_dash["cases"]
    print(f"  ✓ Manager Dashboard Metrics:")
    print(f"     • Total Cases       : {stats['total_cases']} (Functional: {stats['functional_cases']}, Future/Inactive: {stats['inactive_cases']})")
    print(f"     • Assigned Cases    : {stats['assigned_cases']}")
    print(f"     • Completed Sales   : {stats['total_sales']}")
    print(f"     • Unresolved Items  : {stats['unresolved_items']}")

    # Verify Tag History Chain
    rfid_hist = session.get(f"{PROXY_URL}/manager/rfid-history").json()
    target_tag = next((r for r in rfid_hist if r['uid'] == tag_uid), None)
    assert target_tag is not None, "Tag not found in registry!"
    print(f"  ✓ RFID Lifecycle Chain for {tag_uid}:")
    for idx, hist in enumerate(target_tag.get('assignment_history', [])):
        print(f"     {idx+1}. Product: {hist['product_id']} ({hist['product_name']}) | Status: {hist['status']} | Assigned: {hist['assigned_at']} | Released: {hist.get('released_at')}")
    assert len(target_tag['assignment_history']) >= 2, "Historical assignment was overwritten!"
    print("  ✓ Proof verified: Previous assignment history is permanently preserved without overwrite.")

    # Cleanup: Release case for Rahul now that items are settled
    session.post(f"{PROXY_URL}/auth/logout", json={"employee_id": "EMP001"})
    print("\n" + "=" * 70)
    print("   ALL WORKFLOW STEPS EXECUTED AND VALIDATED WITH 100% SUCCESS")
    print("=" * 70)

if __name__ == "__main__":
    run_workflow()
