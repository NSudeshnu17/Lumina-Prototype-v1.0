# Technical Specification & Whitepaper: Architecture, Tech Stack, Components & Dependencies
## Lumina RFID — Smart Jewellery Store Handling & Monitoring System (Phase 1)

**Document Type:** Formal Technical Whitepaper & Architectural Specification  
**System Name:** Lumina RFID  
**Target Release:** Phase-1 Production Prototype  
**Date of Technical Review:** October 8, 2026  
**Audience:** Chief Technology Officers (CTO), Lead System Architects, Technical Evaluators, Full-Stack Engineers  

---

## 1. Executive Technical Overview

**Lumina RFID** is a specialized, custodial inventory and workflow management solution developed specifically for fine luxury jewellery stores. The system addresses the unique operational risks of high-value inventory handling: untracked removal of pieces from display cases, custodial ambiguity during sales presentations, manual ledger reconciliations, and the complexities of physical RFID tag lifecycle management.

To achieve maximum reliability with zero unnecessary enterprise-level bloat, the software was engineered around a disciplined, lightweight, and modern technology stack:
- **Presentation Layer:** React.js 18 with Vite build tooling and React Router v7.
- **Styling Architecture:** High-performance, tokenized Vanilla CSS (zero external UI framework runtime overhead).
- **Application Services Layer:** Python 3.14+ with Flask 3.1 REST API framework.
- **Persistence & Transaction Engine:** SQLite 3 with Write-Ahead Logging (WAL) and enforced Foreign Key constraints.
- **Hardware Integration Layer:** USB HID (Human Interface Device) keyboard emulation with an application-level context engine and software debounce logic.

---

## 2. Comprehensive Technology Stack & Dependency Matrix

The application strictly avoids heavy enterprise frameworks (such as Docker, Redux, JWT microservices, Kubernetes, or heavyweight component libraries like Material UI or Ant Design) in favor of deterministic, auditable, and easily maintainable native components.

### 2.1 Complete Component & Dependency Breakdown

| Layer | Technology / Library | Version | Exact Purpose in Lumina RFID | Architectural Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Runtime** | **Node.js** | 20+ / 22+ | Host environment for frontend bundling and Vite development proxy. | Industry standard execution environment for modern JavaScript toolchains. |
| **Frontend Framework** | **React.js (`react`, `react-dom`)** | 18.3.1 | Core component lifecycle, reactive state management (`useState`, `useEffect`, `useRef`, `useCallback`). | Virtual DOM provides instant UI updates upon hardware scans without page reloads. |
| **Frontend Bundler** | **Vite (`@vitejs/plugin-react`)** | 8.3.3 | Fast Hot Module Replacement (HMR), optimized Rollup production bundling, and development reverse proxy. | Eliminates manual Webpack configuration; native ES module compilation provides instantaneous dev server start. |
| **Frontend Routing** | **React Router (`react-router-dom`)** | 7.x | Declarative client-side routing across `/admin/*`, `/salesperson/*`, and `/manager/*`. | Enables seamless navigation while preserving application state and RFID reader autofocus contexts. |
| **Styling Engine** | **Vanilla CSS (`index.css`)** | Custom Tokens | Design tokens, responsive grid layouts, custom badges, RFID pulses, and modal dialogs. | Zero runtime CSS-in-JS overhead; total control over rendering performance and aesthetic consistency. |
| **Backend Runtime** | **Python** | 3.14+ (64-bit) | Backend script and API execution runtime. | Robust standard library, native SQLite binding, and rapid REST API implementation. |
| **Backend Web Framework**| **Flask** | 3.1.1 | HTTP request routing, blueprint modularization, session management, and JSON serialization. | Minimalist micro-framework with negligible overhead compared to Django or FastAPI. |
| **Cross-Origin Bridge** | **Flask-CORS (`flask-cors`)** | 5.0.1 | Cross-Origin Resource Sharing middleware enabling authenticated requests from Vite (`:5173`) to Flask (`:5000`). | Ensures secure browser origin validation during local development and testing. |
| **Database Engine** | **SQLite 3 (`sqlite3`)** | Standard Library | Local relational database stored in `jewellery.db`. | Zero-configuration, zero-dependency embedded database supporting full ACID transactions and SQL queries. |
| **Database Performance** | **SQLite WAL Mode** | Native PRAGMA | Write-Ahead Logging enabled via `PRAGMA journal_mode = WAL;`. | Allows concurrent readers without blocking write transactions during rapid scans. |
| **Data Integrity Engine** | **SQLite Foreign Keys** | Native PRAGMA | Enforced via `PRAGMA foreign_keys = ON;`. | Guarantees referential integrity between products, tag assignments, cases, and employees. |
| **Document Generation** | **python-docx** | 1.2.0 | Automated compiler for Word (`.docx`) technical reports and executive documentation. | Programmatic document creation directly from system specifications without third-party office suites. |

---

## 3. Detailed Component Architecture & Directory Structure

```text
C:\Users\Admin\Downloads\Sudeshnu\Lumina_RFID\
│
├── backend/
│   ├── app.py                      # Flask Application Entry Point & Blueprint Registration
│   ├── config.py                   # Centralized Configuration (Paths, Secret Keys)
│   ├── requirements.txt            # Python Dependencies Specification
│   │
│   ├── database/
│   │   ├── db.py                   # Database Connection Pool, Row Factories & Dict Helpers
│   │   ├── init_db.py              # DDL Schema Creation & Clean Baseline Initialization
│   │   └── jewellery.db            # Embedded SQLite Database Storage File
│   │
│   ├── routes/
│   │   ├── auth_routes.py          # Session Auth, RFID Staff Login, Case Release
│   │   ├── admin_routes.py         # Staff & Product Registration, Tag Reassignment, Registry Views
│   │   ├── salesperson_routes.py   # Active Desk Dashboard, Item Scan (Remove/Return)
│   │   ├── billing_routes.py       # Billing Desk Counter, Cancellation, Sale Completion
│   │   └── manager_routes.py       # Manager Dashboard Statistics, Case & Audit Histories
│   │
│   └── services/
│       ├── rfid_service.py         # Central RFID Registry & Assignment Lifecycle Lookup
│       ├── case_service.py         # Priority Case Allocation Algorithm (CASE-01 to CASE-03)
│       ├── product_service.py      # Mandatory Product Lifecycle State Machine Engine
│       ├── billing_service.py      # Atomic Multi-Table Sale & Invoice Finalization Engine
│       └── log_service.py          # Immutable Audit Trail Logger & Aggregate Metrics Service
│
├── frontend/
│   ├── package.json                # NPM Package Manifest & Script Definitions
│   ├── vite.config.js              # Vite Development Proxy Configuration (/api -> :5000)
│   ├── index.html                  # HTML5 Application Shell
│   │
│   └── src/
│       ├── main.jsx                # React DOM Mount Entry Point
│       ├── App.jsx                 # Top-Level BrowserRouter & Role-Based Route Definitions
│       ├── index.css               # Design System, Design Tokens, Layout Grids, Animations
│       │
│       ├── api/
│       │   └── api.js              # Client-Side HTTP API Gateway Wrapper (Fetch API)
│       │
│       ├── components/
│       │   ├── RFIDInput.jsx       # Reusable Context-Aware RFID Hardware Input & Debouncer
│       │   └── Navbar.jsx          # Header Navigation & Breadcrumb Component
│       │
│       └── pages/
│           ├── Home/
│           │   └── Home.jsx        # Landing Portal with 3 Role Modules (Admin, Salesperson, Manager)
│           ├── Admin/
│           │   └── AdminPortal.jsx # Multi-Tab Admin Interface (Staff, Products, Billing, Cases, Logs)
│           ├── Salesperson/
│           │   ├── SalespersonLogin.jsx     # Fast RFID Badge Authentication Gateway
│           │   └── SalespersonDashboard.jsx # Active Case Handling Desk with Real-Time Inventory
│           └── Manager/
│               ├── ManagerLogin.jsx         # Manager RFID Badge Security Gate
│               └── ManagerDashboard.jsx     # Executive Store Oversight, 5-Case Grid & Audit Chains
│
├── docs/                           # Dedicated Documentation Repository
│   ├── PROJECT_REPORT.md           # Master Project Specification Report
│   ├── TECHNICAL_WHITEPAPER.md     # In-Depth Technical Specification (This File)
│   ├── EXECUTIVE_BRIEFING.md       # High-Level Presentation Briefing for Officials
│   ├── Lumina_RFID_Project_Report.docx # Formatted Word Document with Embedded Diagrams
│   ├── generate_docx.py            # Automated Compilation Script for Word Reports
│   └── *.jpg                       # Generated High-Resolution Architectural & Flow Diagrams
│
├── e2e_full_workflow.py            # Comprehensive 11-Step Automated E2E Test Suite
├── view_db.py                      # Real-Time CLI SQLite Table Inspection Tool
└── README.md                       # Comprehensive Execution & Operation Manual
```

---

## 4. Frontend Layer Architecture (React.js & Vite)

### 4.1 Client Application Flow & Routing (`App.jsx`)
The frontend is constructed as a Single Page Application (SPA) utilizing `react-router-dom` v7. Client-side navigation ensures that browser state, open hardware focus, and memory cache remain persistent across operational transitions.

```text
/ (Home)
 ├── /admin                   -> AdminPortal.jsx (Employee Reg, Product Reg, Billing Counter, Cases, Registry, Logs)
 ├── /salesperson/login       -> SalespersonLogin.jsx (Badge Scan)
 ├── /salesperson/dashboard   -> SalespersonDashboard.jsx (Active Case Inventory, Remove/Return Desk)
 ├── /manager/login           -> ManagerLogin.jsx (Manager Badge Scan)
 └── /manager/dashboard       -> ManagerDashboard.jsx (Real-time Oversight, 5-Case Matrix, Audit Histories)
```

### 4.2 Reusable Context-Aware RFID Hardware Input (`RFIDInput.jsx`)
Because tabletop USB RFID readers emulate USB HID keyboards by typing the card UID followed by a carriage return (`Enter`), standard text fields would suffer from input focus loss, accidental duplicate submissions, and context ambiguity.

The `RFIDInput` component solves this through three dedicated architectural mechanisms:
1. **Continuous Visual Context Badging**: Displays the active application reader mode (e.g., `CASE-01 ITEM HANDLING`, `BILLING`, `PRODUCT_REGISTRATION`) with animated CSS pulse indicators.
2. **Deterministic Focus Management**: Leverages React `useRef` and `useEffect` to ensure the text input automatically retains focus upon mounting or mode changes without user intervention.
3. **Hardware Debounce Engine (2000ms)**: Physical RF antennas emit repeated UID strings when a card is held in the electromagnetic field for longer than 200ms. The component stores `{ uid: string, time: number }` in component state; repeated scans of the exact same UID within 2 seconds are intercepted and discarded before triggering backend mutations.

```javascript
// Hardware Debounce Implementation in RFIDInput.jsx
const handleSubmit = useCallback(async (e) => {
  e && e.preventDefault();
  const trimmed = uid.trim();
  if (!trimmed) {
    setFeedback({ type: 'error', text: 'RFID UID cannot be empty.' });
    return;
  }

  // 2-Second Debounce Protection
  const now = Date.now();
  if (trimmed === lastScan.uid && now - lastScan.time < 2000) {
    setFeedback({ type: 'warning', text: 'Duplicate scan ignored (debounce).' });
    setUid('');
    return;
  }

  setLastScan({ uid: trimmed, time: now });
  // Pass to parent handler...
}, [uid, onScan, lastScan]);
```

### 4.3 Centralized Client API Gateway (`api/api.js`)
All communication with the Flask backend is channeled through an asynchronous API client using the standard browser `fetch` API. It enforces JSON serialization, sets `credentials: 'include'` for cookie and session persistence, and formats structured error responses.

### 4.4 Design System & Styling Architecture (`index.css`)
Built purely with modern Vanilla CSS, the styling utilizes custom CSS custom properties (CSS variables) for design tokens:
- Primary brand hues: `#0F172A` (Navy/Slate) and `#1E3A8A` (Deep Blue).
- State status indicators: `#16A34A` (`AVAILABLE`), `#D97706` (`IN_HANDLING`), `#DC2626` (`BILLING`), `#475569` (`SOLD`).
- Micro-animations: Hardware pulse indicators utilizing CSS keyframe animations.
- Responsive design: CSS Grid (`grid-template-columns: repeat(auto-fit, minmax(...))`) ensuring responsive operation across laptops, POS touch displays, and management tablets.

---

## 5. Backend Layer Architecture (Python & Flask)

### 5.1 Service-Oriented Blueprint Modularization
The Flask application is decoupled into five distinct functional blueprints, delegating business logic to independent service modules:

```text
Flask Request (:5000)
    │
    ├── auth_bp (/api/auth/*)        --> case_service.py (Auto-Allocation / Case Release)
    ├── admin_bp (/api/admin/*)      --> product_service.py & rfid_service.py
    ├── sp_bp (/api/salesperson/*)   --> product_service.py (Item Scan / State Machine)
    ├── billing_bp (/api/billing/*)  --> billing_service.py (Atomic Sale Transactions)
    └── manager_bp (/api/manager/*)  --> log_service.py & case_service.py
```

### 5.2 Priority Case Allocation Engine (`case_service.py`)
To prevent store floor conflict, the allocation engine enforces three non-negotiable business rules:
1. **Single Case per Employee**: An employee cannot hold simultaneous allocations across multiple cases.
2. **Single Employee per Case**: A display case cannot be allocated to more than one active salesperson concurrently.
3. **Deterministic Priority Queue**: Available functional cases are assigned sequentially (`CASE-01` first, followed by `CASE-02`, then `CASE-03`). Future/inactive cases (`CASE-04` and `CASE-05`) are permanently ignored by the auto-allocator.

```python
# Priority Case Allocation Algorithm in case_service.py
for case_id in ['CASE-01', 'CASE-02', 'CASE-03']:
    case = db.execute("SELECT * FROM cases WHERE case_id=? AND functional=1", (case_id,)).fetchone()
    if not case:
        continue
    active = db.execute("SELECT id FROM case_assignments WHERE case_id=? AND status='ACTIVE'", (case_id,)).fetchone()
    if not active:
        # Commit Allocation
        db.execute("INSERT INTO case_assignments (case_id, employee_id, assigned_at, status) VALUES (?,?,?,?)",
                   (case_id, employee_id, now, 'ACTIVE'))
        db.execute("UPDATE cases SET current_status='ASSIGNED' WHERE case_id=?", (case_id,))
        db.commit()
        return case_id, None
```

### 5.3 Mandatory Product Lifecycle State Machine (`product_service.py`)
Jewellery pieces follow a formal finite state automaton. Transitions outside the defined graph are rejected by the backend with HTTP 409 Conflict.

```text
                        ┌──────────────┐
                        │  AVAILABLE   │
                        └──────┬───────┘
                     Remove    │   ▲ Return
                      Item     │   │  Item
                               ▼   │
                        ┌──────────────┐
                        │ IN_HANDLING  │
                        └──────┬───────┘
                     Billing   │   ▲ Cancel
                      Scan     │   │ Billing
                               ▼   │
                        ┌──────────────┐
                        │   BILLING    │
                        └──────┬───────┘
                     Complete  │
                       Sale    ▼
                        ┌──────────────┐
                        │     SOLD     │
                        └──────────────┘
```

Allowed State Transitions:
- `AVAILABLE` $\rightarrow$ `IN_HANDLING` (Custody transferred to salesperson)
- `IN_HANDLING` $\rightarrow$ `AVAILABLE` (Safe return to display case)
- `IN_HANDLING` $\rightarrow$ `BILLING` (Item moved to billing counter)
- `BILLING` $\rightarrow$ `IN_HANDLING` (Billing cancelled by cashier)
- `BILLING` $\rightarrow$ `SOLD` (Sale finalized, tag released)

Illegal Transitions (Strictly Rejected by Engine):
- `AVAILABLE` $\rightarrow$ `SOLD` (Bypasses custodial handover and billing)
- `AVAILABLE` $\rightarrow$ `BILLING` (Cannot bill an item currently sitting in an untouched case)
- `SOLD` $\rightarrow$ `AVAILABLE` (Permanent business record cannot be resurrected)
- `SOLD` $\rightarrow$ `IN_HANDLING` (Cannot handle items that have left the store)

---

## 6. Persistence & Relational Data Layer (SQLite 3)

### 6.1 Relational Architecture & ACID Compliance
The backend database is initialized via `backend/database/init_db.py`. To ensure durability and zero corruption during rapid scanning, the database connection executes:
- `PRAGMA foreign_keys = ON;` (Guarantees referential integrity)
- `PRAGMA journal_mode = WAL;` (Enables concurrent readers alongside writing threads)

### 6.2 Relational Schema Definition

#### 1. `employees` Table
Stores staff member credentials, system roles, and assigned employee badge RFIDs.
* Columns: `id`, `employee_id` (UNIQUE), `name`, `role` (`ADMIN`, `MANAGER`, `SALESPERSON`), `section`, `rfid_uid` (UNIQUE), `active`, `created_at`, `updated_at`.

#### 2. `rfid_registry` Table
The central registry distinguishing employee credentials from jewellery item tags.
* Columns: `id`, `uid` (UNIQUE), `rfid_type` (`EMPLOYEE`, `ITEM_TAG`), `status` (`ACTIVE`, `ASSIGNED`, `RELEASED`), `created_at`, `updated_at`.

#### 3. `cases` Table
Tracks all physical display cabinets in the store.
* Columns: `id`, `case_id` (UNIQUE, `CASE-01` to `CASE-05`), `name`, `functional` (`1` for cases 01–03, `0` for cases 04–05), `current_status` (`AVAILABLE`, `ASSIGNED`), `created_at`.

#### 4. `case_assignments` Table
Preserves the complete, historical chain of staff case allocations.
* Columns: `id`, `case_id`, `employee_id`, `assigned_at`, `released_at`, `status` (`ACTIVE`, `COMPLETED`).
* *Crucial Rule:* Records in this table are never overwritten; when a staff member logs out, `released_at` is stamped and `status` moves to `COMPLETED`.

#### 5. `products` Table
Permanent inventory records of all store jewellery.
* Columns: `id`, `product_id` (UNIQUE), `product_name`, `category`, `weight`, `price`, `case_id`, `current_status` (`AVAILABLE`, `IN_HANDLING`, `BILLING`, `SOLD`), `current_handler_employee_id`, `created_at`, `sold_at`, `updated_at`.

#### 6. `tag_assignments` Table
Maintains the relational mapping between reusable physical RFID tags and permanent jewellery products.
* Columns: `id`, `rfid_uid`, `product_id`, `assigned_at`, `released_at`, `status` (`ACTIVE`, `RELEASED`).

#### 7. `product_state_history` Table
Immutable chronological ledger recording every state transition.
* Columns: `id`, `product_id`, `old_state`, `new_state`, `employee_id`, `case_id`, `timestamp`, `reason`.

#### 8. `activity_logs` Table
General audit trail capturing all system events with exact server timestamps.
* Columns: `id`, `timestamp`, `employee_id`, `role`, `action` (`LOGIN`, `LOGOUT`, `CASE_ASSIGNED`, `ITEM_REMOVED`, `SALE_COMPLETED`, etc.), `case_id`, `product_id`, `rfid_uid`, `details`.

#### 9. `sales` Table
Finalized transaction records with sequential billing numbers.
* Columns: `id`, `bill_number` (UNIQUE, `BILL-0001`...), `product_id`, `employee_id`, `customer_name`, `customer_phone`, `amount`, `created_at`, `status`.

---

## 7. Core Business Logic & Innovations

### 7.1 Reusable Physical RFID Tags vs. Permanent Business Entities
A fundamental innovation of the Lumina RFID architecture is the strict decoupling of **Physical RFID Tags** from **Jewellery Product Records**.

In physical retail:
- A jewellery piece (`JWL001`, Gold Ring) is a permanent legal business entity that must be stored in financial history forever.
- An RFID tag (`TAG001`) is a physical piece of silicon that costs money and must be recycled once an item is purchased and boxed.

When a sale is completed in `billing_service.py`:
1. `products.current_status` becomes `SOLD` and `sold_at` is stamped.
2. The active `tag_assignments` record is closed by populating `released_at` and setting `status = 'RELEASED'`.
3. `rfid_registry.status` transitions from `ASSIGNED` to `RELEASED`.
4. *Crucial:* The original `tag_assignments` row is **never deleted or overwritten**.

When the same physical tag is scanned during a future registration:
1. The system checks `rfid_registry`. It detects the tag is in `RELEASED` status.
2. It fetches historical assignments from `tag_assignments` and displays:
   > "RFID AVAILABLE FOR REUSE: Previously bound to JWL001 (SOLD on 2026-10-07). Confirm Reassignment to JWL007?"
3. Upon confirmation, a **brand new row** is inserted into `tag_assignments` linking `TAG001` to `JWL007`.
4. Result: Both historical relationships (`TAG001` $\rightarrow$ `JWL001` and `TAG001` $\rightarrow$ `JWL007`) remain in the database permanently.

### 7.2 Preventative Logout Validation (Custodial Anti-Shrink Engine)
To prevent staff from clocking out while high-value merchandise is still unreturned or unbilled, the `release_case` service interrogates the inventory table before allowing session termination:

```python
# Custodial Anti-Shrink Check in case_service.py
unresolved = db.execute(
    "SELECT product_id, product_name, current_status FROM products "
    "WHERE current_handler_employee_id=? AND current_status IN ('IN_HANDLING', 'BILLING')",
    (employee_id,)
).fetchall()

if unresolved:
    return None, {
        "message": "LOGOUT BLOCKED: You still have unresolved jewellery items.",
        "items": [dict(row) for row in unresolved]
    }
```
If unresolved items exist, logout is blocked with HTTP 409, and the frontend displays the list of items that must be returned or billed.

### 7.3 Multi-Table Atomic Transactions
Operations that alter state across multiple tables are executed inside explicit SQLite transactions (`try ... db.commit() except: db.rollback()`). 

During a sale completion, five distinct database mutations occur simultaneously:
1. Product state transitions to `SOLD`.
2. Sales record is created with an auto-incrementing invoice number.
3. Active tag assignment is marked `RELEASED`.
4. Central RFID registry status is updated to `RELEASED`.
5. State history and audit logs are recorded.

If any single step fails, the entire transaction rolls back, preventing orphaned records.

---

## 8. Automated Verification & Inspection Tooling

To ensure the system can be validated without manual UI testing, two dedicated verification utilities are integrated directly into the repository root:

### 8.1 Automated Integration Test Suite (`e2e_full_workflow.py`)
An automated end-to-end Python test script that connects to the live Vite proxy (`http://localhost:5173/api`) and executes all 11 core lifecycle operations:
1. Health and reverse proxy verification.
2. Employee registration & duplicate validation.
3. Product registration & active tag collision blocking.
4. Salesperson badge authentication & priority allocation (`CASE-01`).
5. Single-reader item removal (`AVAILABLE` $\rightarrow$ `IN_HANDLING`).
6. Single-reader item return (`IN_HANDLING` $\rightarrow$ `AVAILABLE`).
7. Custodial logout block verification.
8. Admin billing scan (`IN_HANDLING` $\rightarrow$ `BILLING`) & cancellation recovery.
9. Atomic sale finalization (`BILLING` $\rightarrow$ `SOLD`), bill generation, and tag release.
10. Explicit tag reassignment confirmation workflow.
11. Full Manager audit trail verification across all 5 cases.

Execution command:
```powershell
.\backend\venv\Scripts\python.exe e2e_full_workflow.py
```

### 8.2 Real-Time Database Inspector (`view_db.py`)
A command-line database inspection utility that formats and outputs all 8 database tables with aligned headers, timestamps, and relational foreign key values:
```powershell
.\backend\venv\Scripts\python.exe view_db.py
```

---

## 9. Conclusion

The **Lumina RFID Phase-1 Technical Architecture** provides a robust, production-grade proof of concept for luxury retail asset tracking. By utilizing a disciplined technology stack—React 18, Vite, Python Flask, and SQLite—the system proves that complex custodial accountability, context-aware hardware abstraction, and immutable audit logging can be achieved with exceptional speed, stability, and zero unnecessary operational complexity.
