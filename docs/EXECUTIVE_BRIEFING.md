# Executive Summary & Presentation Briefing
## Lumina RFID — Smart Jewellery Store Handling & Monitoring Prototype

---

### Overview for Decision Makers
**Lumina RFID** is a smart handling and custodial security system for fine jewellery stores. 

In luxury retail, a single missing piece can lead to substantial financial loss. Lumina RFID automates item movement tracking, establishes clear salesperson accountability, prevents stock misplacement, and preserves historical records through RFID automation.

---

### Key Capabilities Demonstrated in Phase 1

1. **Custodial Chain of Custody**
   - Salespersons authenticate with RFID badges.
   - The system automatically allocates display cases (`CASE-01` → `CASE-02` → `CASE-03`).
   - Removing an item records the salesperson as the custodian.
   - Salespersons **cannot log out** until all handled items are either returned to the case or billed.

2. **Single-Reader Hardware Innovation**
   - The entire store workflow is demonstrated using **one commercial tabletop USB RFID reader**.
   - Context-aware RFID Reader Modes (`SALESPERSON_LOGIN`, `ITEM_HANDLING`, `BILLING`, `PRODUCT_REGISTRATION`) interpret scans based on the active screen and session.

3. **Strict Product State Machine**
   - Every jewellery piece moves through strict, non-skippable stages:
     $$\text{AVAILABLE} \longleftrightarrow \text{IN\_HANDLING} \longleftrightarrow \text{BILLING} \longrightarrow \text{SOLD}$$
   - Direct, unrecorded moves to `SOLD` or `BILLING` are blocked.

4. **Tag Reusability with Historical Preservation**
   - Physical RFID tags are released upon sale completion.
   - Tags can be reassigned to new jewellery inventory.
   - Historical records are **never overwritten**—the full chain of custody is permanently preserved.

5. **Complete Management Audit Trail**
   - Real-time dashboard displays case occupancy, active staff, inventory status, and unresolved item alerts.
   - Server-side timestamps are recorded for every state change, case allocation, and sale.

---

### Operational Architecture & Tech Stack

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                              REACT.JS (VITE)                           │
 │        • Admin Module    • Salesperson Desk    • Manager Dashboard     │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ JSON REST API (:5173 -> :5000)
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                            PYTHON FLASK BACKEND                        │
 │     • Auth Engine    • Case Allocation    • Product State Machine      │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Atomic Transactions
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                              SQLITE DATABASE                           │
 │     • 5 Display Cases    • Registry & Tag Chains    • Audit Logs       │
 └────────────────────────────────────────────────────────────────────────┘
```

---

### Phase-2 Vision (Smart Cases)
Phase 1 validates the business logic and database architecture. Phase 2 extends this logic to:
- Individual smart display cabinets with embedded RFID antennas.
- Electronic tray locks that release upon salesperson badge authorization.
- Real-time inventory sensing across all cases.
