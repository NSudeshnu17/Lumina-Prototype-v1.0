"""Case service — case allocation and release."""
from database.db import get_db, dict_from_row, dicts_from_rows
from datetime import datetime

def get_all_cases():
    """Get all cases with current assignment info."""
    db = get_db()
    try:
        cases = dicts_from_rows(db.execute("SELECT * FROM cases ORDER BY case_id").fetchall())
        for c in cases:
            assignment = dict_from_row(db.execute(
                "SELECT ca.*, e.name as employee_name FROM case_assignments ca "
                "JOIN employees e ON ca.employee_id = e.employee_id "
                "WHERE ca.case_id=? AND ca.status='ACTIVE'", (c['case_id'],)
            ).fetchone())
            c['current_assignment'] = assignment
            products = dicts_from_rows(db.execute(
                "SELECT product_id, product_name, current_status FROM products WHERE case_id=?",
                (c['case_id'],)
            ).fetchall())
            c['products'] = products
            c['product_count'] = len(products)
        return cases
    finally:
        db.close()

def allocate_case(employee_id):
    """Allocate first available functional case to employee. Returns (case_id, error)."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if employee already has active assignment
        existing = dict_from_row(db.execute(
            "SELECT * FROM case_assignments WHERE employee_id=? AND status='ACTIVE'",
            (employee_id,)
        ).fetchone())
        if existing:
            return existing['case_id'], None  # Resume existing

        # Find first available functional case
        for case_id in ['CASE-01', 'CASE-02', 'CASE-03']:
            case = dict_from_row(db.execute(
                "SELECT * FROM cases WHERE case_id=? AND functional=1", (case_id,)
            ).fetchone())
            if not case:
                continue
            active = db.execute(
                "SELECT id FROM case_assignments WHERE case_id=? AND status='ACTIVE'",
                (case_id,)
            ).fetchone()
            if not active:
                # Allocate this case
                db.execute(
                    "INSERT INTO case_assignments (case_id, employee_id, assigned_at, status) VALUES (?,?,?,?)",
                    (case_id, employee_id, now, 'ACTIVE')
                )
                db.execute("UPDATE cases SET current_status='ASSIGNED' WHERE case_id=?", (case_id,))
                db.execute(
                    "INSERT INTO activity_logs (timestamp, employee_id, role, action, case_id, details) VALUES (?,?,?,?,?,?)",
                    (now, employee_id, 'SALESPERSON', 'CASE_ASSIGNED', case_id, f'{employee_id} assigned to {case_id}')
                )
                db.commit()
                return case_id, None

        return None, "NO CASE CURRENTLY AVAILABLE. All functional cases are currently assigned."
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def release_case(employee_id):
    """Release case assignment for employee."""
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        assignment = dict_from_row(db.execute(
            "SELECT * FROM case_assignments WHERE employee_id=? AND status='ACTIVE'",
            (employee_id,)
        ).fetchone())
        if not assignment:
            return None, "No active case assignment found."

        case_id = assignment['case_id']

        # Check for unresolved items
        unresolved = dicts_from_rows(db.execute(
            "SELECT product_id, product_name, current_status FROM products "
            "WHERE current_handler_employee_id=? AND current_status IN ('IN_HANDLING', 'BILLING')",
            (employee_id,)
        ).fetchall())
        if unresolved:
            return None, {"message": "LOGOUT BLOCKED: You still have unresolved jewellery items.", "items": unresolved}

        db.execute(
            "UPDATE case_assignments SET released_at=?, status='COMPLETED' WHERE employee_id=? AND status='ACTIVE'",
            (now, employee_id)
        )
        db.execute("UPDATE cases SET current_status='AVAILABLE' WHERE case_id=?", (case_id,))
        db.execute(
            "INSERT INTO activity_logs (timestamp, employee_id, role, action, case_id, details) VALUES (?,?,?,?,?,?)",
            (now, employee_id, 'SALESPERSON', 'CASE_RELEASED', case_id, f'{employee_id} released {case_id}')
        )
        db.commit()
        return case_id, None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_case_assignment_history():
    """Get all case assignments (historical)."""
    db = get_db()
    try:
        return dicts_from_rows(db.execute(
            "SELECT ca.*, e.name as employee_name FROM case_assignments ca "
            "JOIN employees e ON ca.employee_id = e.employee_id "
            "ORDER BY ca.assigned_at DESC"
        ).fetchall())
    finally:
        db.close()
