# Lumina RFID — Smart Jewellery Store Handling System (Phase 1)

A working full-stack prototype of an RFID-based Jewellery Store Smart Handling and Monitoring System designed for high auditability, single-reader hardware simulation, and complete lifecycle tracking.

---

## 1. Project Overview & Prototype Scope

In Phase 1, physical smart-case microcontrollers, electronic solenoids, and multiple antennas are simulated using **one physical USB RFID Reader** connected to a Windows laptop. 

- **Application-Level RFID Reader Modes**: Since only one reader exists, the active page and user session contextualize the meaning of an RFID scan (`SALESPERSON_LOGIN`, `ITEM_HANDLING`, `BILLING`, `PRODUCT_REGISTRATION`, `EMPLOYEE_REGISTRATION`, etc.).
- **Automatic Priority Case Allocation**: When a salesperson logs in with their RFID badge, the system allocates the first available functional case (`CASE-01` → `CASE-02` → `CASE-03`).
- **Single-Reader Handling Simulation**: When an item tag is scanned on the salesperson's desk, the active salesperson's session determines which display case is modified.
- **RFID Tag Reusability**: Jewellery product records remain permanent in the database, while RFID tags are reusable physical identifiers that transition through `ASSIGNED` → `RELEASED` → `REASSIGNED`.
- **Permanent Audit Trail**: All case allocations, item movements, billing operations, sales, and tag assignments are timestamped and preserved forever.

---

## 2. Technology Stack

- **Frontend**: React 18, Vite, React Router v7, Vanilla CSS
- **Backend**: Python 3.14+, Flask 3.1, Flask-CORS
- **Database**: SQLite with WAL mode, foreign keys, and atomic transactions
- **RFID Support**: USB HID Keyboard-emulating RFID readers or manual UID input

---

## 3. Folder Structure

```text
C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID/
│
├── backend/
│   ├── app.py                     # Main Flask application entry
│   ├── config.py                  # Database & session configuration
│   ├── requirements.txt           # Python backend dependencies
│   ├── test_scenario.py           # Automated end-to-end test suite
│   ├── database/
│   │   ├── db.py                  # SQLite connection helper & row factories
│   │   ├── init_db.py             # Schema definition & baseline initialization
│   │   └── jewellery.db           # SQLite database file
│   ├── routes/
│   │   ├── auth_routes.py         # Login, session, logout, case release
│   │   ├── admin_routes.py        # Staff & product setup, cases, logs
│   │   ├── salesperson_routes.py  # Item scanning & handling
│   │   ├── billing_routes.py      # Billing scan, cancel, complete sale
│   │   └── manager_routes.py      # Store overview, case history, audit logs
│   └── services/
│       ├── rfid_service.py        # Central RFID registry management
│       ├── case_service.py        # Priority allocation & release logic
│       ├── product_service.py     # Product state machine enforcement
│       ├── billing_service.py     # Atomic billing & sale transactions
│       └── log_service.py         # Activity audit queries & dashboard stats
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js             # Vite proxy configuration (/api -> :5000)
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                # Application routes
│       ├── index.css              # Styling system & design tokens
│       ├── api/api.js             # Client API service
│       ├── components/
│       │   ├── Navbar.jsx         # Navigation bar component
│       │   └── RFIDInput.jsx      # Reusable RFID reader input with 2s debounce
│       └── pages/
│           ├── Home/Home.jsx
│           ├── Admin/AdminPortal.jsx
│           ├── Salesperson/SalespersonLogin.jsx
│           ├── Salesperson/SalespersonDashboard.jsx
│           ├── Manager/ManagerLogin.jsx
│           └── Manager/ManagerDashboard.jsx
│
├── docs/
│   ├── PROJECT_REPORT.md          # Comprehensive technical report for officials
│   └── EXECUTIVE_BRIEFING.md      # Executive summary & presentation briefing
│
├── view_db.py                     # Real-time CLI database table inspector
├── e2e_full_workflow.py           # Automated end-to-end integration test runner
└── README.md
```

---

## 4. Setup & Running Instructions (Windows PowerShell)

Open **two separate PowerShell windows** on your Windows laptop.

### Terminal 1: Start Flask Backend Server
```powershell
cd C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID\backend

# 1. Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# 2. Run Flask App
python app.py
```
> The backend server starts on **`http://127.0.0.1:5000`**.

---

### Terminal 2: Start React Frontend Application
```powershell
cd C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID\frontend

# 1. Ensure Node.js path is in environment
$env:Path = "C:\Program Files\nodejs;$env:Path"

# 2. Start Vite Development Server
npm run dev
```
> The web interface starts on **`http://localhost:5173`**.

Open your browser at: **[http://localhost:5173](http://localhost:5173)**.

---

## 5. Step-by-Step Manual Demonstration Workflow

You can test either using **physical RFID cards with your USB reader** or by **typing the UID manually into the RFID input box and pressing Enter**.

### Part A: Admin Setup & Registrations
1. On the Home page, click **Enter Admin Portal →**.
2. **Register a Salesperson** (Employee Setup tab):
   * Scan your staff RFID card on the reader (or type `EMP_CARD_01` and submit).
   * Enter Employee ID: `EMP001`, Name: `Rahul Sharma`, Role: `Salesperson`.
   * Click **Register Employee**. Verify the staff member appears in the Active Directory.
3. **Register a Manager**:
   * Enter Employee ID: `MGR001`, Name: `Pooja Verma`, Role: `Manager`, Card UID: `MGR_CARD_01`.
   * Click **Register Employee**.
4. **Register Jewellery Item** (Product Registration tab):
   * Scan an item RFID tag (or type `TAG001` and submit).
   * Enter Product ID: `JWL001`, Name: `22K Gold Solitaire Ring`, Price: `45000`, Case: `CASE-01` (Functional).
   * Click **Register Item & Bind RFID**. Item is registered with status `AVAILABLE`.
5. Click **← Back** in the top navigation bar to return to Home.

### Part B: Salesperson Login & Automatic Case Allocation
1. From the Home page, click **Salesperson Login →**.
2. Scan Rahul's card (`EMP_CARD_01`) on the reader (or type it and submit).
3. **Verified Result**:
   * Rahul is identified.
   * System automatically allocates **`CASE-01`** (first functional case available).
   * Opens **Salesperson Dashboard** showing `CASE-01` and item `JWL001` (`AVAILABLE`).

### Part C: Single-Reader Item Handling & Safety Validation
1. On Salesperson Dashboard under **Physical Item Handling Scanner** (Mode: `CASE-01 ITEM HANDLING`):
   * **Scan 1 (Remove Item)**: Scan `TAG001` → Status: `AVAILABLE` → `IN_HANDLING` (*Item out for customer display*).
   * **Scan 2 (Return Item)**: Scan `TAG001` → Status: `IN_HANDLING` → `AVAILABLE` (*Item safely returned to case*).
   * **Scan 3 (Take Out for Sale)**: Scan `TAG001` → Status: `AVAILABLE` → `IN_HANDLING`.
2. **Test Preventative Logout Block**:
   * Click **Release Case & Logout**.
   * **Verified Result**: Logout is **blocked** because `JWL001` is still in handling!
3. Click brand name **LUMINA RFID** to return to Home.

### Part D: Admin Billing Counter & Tag Release
1. Click **Enter Admin Portal →** and select **Billing Counter** tab.
2. In the RFID reader box (Mode: `BILLING`), scan `TAG001`.
   * **Verified Result**: Product moves `IN_HANDLING` → `BILLING`. Session loads Product `JWL001` and Handler Rahul.
3. Fill Customer Name (`Amit Patel`) and Phone (`9876543210`).
4. Click **Complete Sale & Release Tag**.
   * **Verified Result**: 
     - Product moves `BILLING` → `SOLD`.
     - Sequential invoice generated (e.g. `BILL-0001`).
     - **Tag `TAG001` is released for reuse**.

### Part E: RFID Tag Reuse (Reassigning Released Tag)
1. Still in Admin Portal, switch to **Product Registration** tab.
2. Enter details for a new item:
   * Product ID: `JWL002`, Name: `Diamond Pendant`, Case: `CASE-02`, RFID UID: `TAG001` *(the same tag just sold!)*.
3. Click **Register Item & Bind RFID**.
4. **Verified Result**: System recognizes `TAG001` is **RELEASED** from sold item `JWL001`. An **RFID AVAILABLE FOR REUSE** modal appears.
5. Click **Confirm Reassign**: `TAG001` is bound to `JWL002`, while its historical assignment to `JWL001` is preserved.

### Part F: Manager Portal & Full Audit Trail
1. Return to Home and click **Manager Portal →**.
2. Scan the Manager card (`MGR_CARD_01`).
3. Inspect the Dashboard tabs:
   * **Case Status View**: Live status of all 5 cases (3 functional, 2 inactive).
   * **Case Allocation History**: Preserved login and case release records.
   * **Product State History**: Full lifecycle transitions (`AVAILABLE` → `IN_HANDLING` → `BILLING` → `SOLD`).
   * **RFID Reuse History**: Shows the full chain for `TAG001` (`JWL001` → `JWL002`).
   * **Full System Audit Trail**: Complete timestamped audit logs.

---

## 6. Real-Time Database Inspection Tool

Inspect all tables and audit records in real-time by running the database viewer in PowerShell:

```powershell
cd C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID
.\backend\venv\Scripts\python.exe view_db.py
```

This outputs formatted tables for:
1. `CASES`
2. `EMPLOYEES`
3. `CASE ALLOCATIONS`
4. `PRODUCTS`
5. `TAG ASSIGNMENT HISTORY`
6. `COMPLETED SALES`
7. `PRODUCT STATE TRANSITIONS`
8. `SYSTEM AUDIT TRAIL`

---

## 7. Automated Integration Test Suite

Run the automated integration test script:

```powershell
cd C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID
.\backend\venv\Scripts\python.exe e2e_full_workflow.py
```

---

## 8. Resetting to a Clean Database

To wipe the database back to a clean baseline:

```powershell
cd C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID
Remove-Item -Path ".\backend\database\jewellery.db*" -Force -ErrorAction SilentlyContinue
.\backend\venv\Scripts\python.exe .\backend\database\init_db.py
```
