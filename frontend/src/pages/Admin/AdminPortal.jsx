import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import RFIDInput from '../../components/RFIDInput';
import { api } from '../../api/api';

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('employees');
  const [employees, setEmployees] = useState([]);
  const [products, setProducts] = useState([]);
  const [cases, setCases] = useState([]);
  const [rfids, setRfids] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form states
  const [empForm, setEmpForm] = useState({ employee_id: '', name: '', role: 'SALESPERSON', section: 'Main Counter', rfid_uid: '' });
  const [prodForm, setProdForm] = useState({ product_id: '', product_name: '', category: 'Gold Ring', weight: '4.5g', price: '35000', case_id: 'CASE-01', rfid_uid: '' });
  
  // Tag Reassignment Modal State
  const [reassignModal, setReassignModal] = useState(null);

  // Billing Tab states
  const [billingProduct, setBillingProduct] = useState(null);
  const [customerForm, setCustomerForm] = useState({ name: '', phone: '' });

  const loadData = async () => {
    try {
      setLoading(true);
      const [e, p, c, r, l] = await Promise.all([
        api.getEmployees(),
        api.getProducts(),
        api.getCases(),
        api.getRfidRegistry(),
        api.getActivityLogs(50)
      ]);
      setEmployees(e);
      setProducts(p);
      setCases(c);
      setRfids(r);
      setLogs(l);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const clearMessages = () => {
    setErrorMsg('');
    setSuccessMsg('');
  };

  // 1. Employee Registration
  const handleEmployeeScan = async (uid) => {
    setEmpForm(prev => ({ ...prev, rfid_uid: uid }));
    return { feedback: { type: 'success', text: `Scanned UID: ${uid}` } };
  };

  const handleRegisterEmployee = async (e) => {
    e.preventDefault();
    clearMessages();
    try {
      const res = await api.registerEmployee(empForm);
      setSuccessMsg(`Employee ${res.employee.name} registered successfully!`);
      setEmpForm({ employee_id: '', name: '', role: 'SALESPERSON', section: 'Main Counter', rfid_uid: '' });
      loadData();
    } catch (err) {
      if (err.code === 'DUPLICATE_EMPLOYEE_RFID') {
        setErrorMsg(`RFID ALREADY REGISTERED: Assigned to ${err.existing_employee?.employee_id} - ${err.existing_employee?.name}`);
      } else if (err.code === 'ITEM_TAG_RFID') {
        setErrorMsg(`INVALID RFID TYPE: This RFID is registered as a Product Tag.`);
      } else {
        setErrorMsg(err.error || 'Failed to register employee');
      }
    }
  };

  // 2. Product Registration
  const handleProductScan = async (uid) => {
    setProdForm(prev => ({ ...prev, rfid_uid: uid }));
    // Pre-check UID status
    try {
      const check = await api.checkRfid(uid);
      if (check.found) {
        if (check.rfid_type === 'EMPLOYEE') {
          return { feedback: { type: 'error', text: `RFID belongs to Employee: ${check.employee?.name}` } };
        } else if (check.rfid_type === 'ITEM_TAG') {
          if (check.status === 'ASSIGNED' && check.active_assignment) {
            return { feedback: { type: 'error', text: `ALREADY REGISTERED to ${check.active_assignment.product_id} (${check.active_assignment.product_name})` } };
          } else if (check.status === 'RELEASED') {
            return { feedback: { type: 'warning', text: `Tag was previously RELEASED. Can be reassigned!` } };
          }
        }
      }
      return { feedback: { type: 'success', text: `RFID UID ${uid} ready for assignment` } };
    } catch (err) {
      return { feedback: { type: 'success', text: `Scanned: ${uid}` } };
    }
  };

  const handleRegisterProduct = async (e) => {
    e.preventDefault();
    clearMessages();
    try {
      const res = await api.registerProduct(prodForm);
      setSuccessMsg(`Product ${res.product.product_id} registered and tag assigned!`);
      setProdForm({ product_id: '', product_name: '', category: 'Gold Ring', weight: '4.5g', price: '35000', case_id: 'CASE-01', rfid_uid: '' });
      loadData();
    } catch (err) {
      if (err.code === 'RFID_RELEASED') {
        // Trigger reuse modal
        setReassignModal({
          uid: prodForm.rfid_uid,
          prev: err.previous_assignments?.[0],
          formData: { ...prodForm }
        });
      } else if (err.code === 'RFID_ASSIGNED') {
        setErrorMsg(`RFID ALREADY REGISTERED to active product ${err.product?.product_id} - ${err.product?.product_name} (${err.product?.current_status}) in ${err.product?.case_id}`);
      } else if (err.code === 'EMPLOYEE_RFID') {
        setErrorMsg(`INVALID RFID TYPE: Registered to Employee ${err.employee?.name}`);
      } else {
        setErrorMsg(err.error || 'Failed to register product');
      }
    }
  };

  const confirmReassign = async () => {
    if (!reassignModal) return;
    try {
      await api.reassignTag(reassignModal.formData);
      setSuccessMsg(`Tag ${reassignModal.uid} successfully reassigned to ${reassignModal.formData.product_id}!`);
      setReassignModal(null);
      setProdForm({ product_id: '', product_name: '', category: 'Gold Ring', weight: '4.5g', price: '35000', case_id: 'CASE-01', rfid_uid: '' });
      loadData();
    } catch (err) {
      setErrorMsg(err.error || 'Failed to reassign tag');
    }
  };

  // 3. Billing Operations
  const handleBillingScan = async (uid) => {
    clearMessages();
    try {
      const res = await api.billingScan(uid);
      setBillingProduct(res.product);
      setSuccessMsg(`Item ${res.product.product_id} moved to BILLING.`);
      loadData();
      return { feedback: { type: 'success', text: `Loaded ${res.product.product_id} into Billing` } };
    } catch (err) {
      if (err.code === 'ALREADY_SOLD') {
        setErrorMsg(`ITEM ALREADY SOLD: ${err.product?.product_id} on Bill ${err.sale?.bill_number}`);
      } else {
        setErrorMsg(err.error || 'Failed to load item for billing');
      }
      throw err;
    }
  };

  const handleCancelBilling = async () => {
    if (!billingProduct) return;
    try {
      await api.cancelBilling(billingProduct.product_id);
      setSuccessMsg(`Billing cancelled for ${billingProduct.product_id}. Returned to IN_HANDLING.`);
      setBillingProduct(null);
      loadData();
    } catch (err) {
      setErrorMsg(err.error || 'Failed to cancel billing');
    }
  };

  const handleCompleteSale = async () => {
    if (!billingProduct) return;
    try {
      const res = await api.completeSale({
        product_id: billingProduct.product_id,
        customer_name: customerForm.name || 'Walk-in Customer',
        customer_phone: customerForm.phone || '9999999999',
        amount: billingProduct.price
      });
      setSuccessMsg(`Sale Completed! Generated ${res.bill_number}. Tag released for reuse.`);
      setBillingProduct(null);
      setCustomerForm({ name: '', phone: '' });
      loadData();
    } catch (err) {
      setErrorMsg(err.error || 'Failed to complete sale');
    }
  };

  return (
    <div>
      <Navbar title="Admin Management Portal" backTo="/" />

      <div className="container">
        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', overflowX: 'auto' }}>
          {[
            { id: 'employees', label: 'Employee Setup' },
            { id: 'products', label: 'Product Registration' },
            { id: 'billing', label: 'Billing Counter' },
            { id: 'cases', label: 'Cases & Allocations' },
            { id: 'rfids', label: 'RFID Registry' },
            { id: 'logs', label: 'Activity Logs' },
          ].map(tab => (
            <button
              key={tab.id}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setActiveTab(tab.id); clearMessages(); }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Global Notifications */}
        {errorMsg && (
          <div className="rfid-feedback rfid-feedback-error" style={{ marginBottom: '1.5rem' }}>
            <strong>Error: </strong> {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="rfid-feedback rfid-feedback-success" style={{ marginBottom: '1.5rem' }}>
            <strong>Success: </strong> {successMsg}
          </div>
        )}

        {/* TAB 1: EMPLOYEE REGISTRATION */}
        {activeTab === 'employees' && (
          <div className="grid-2">
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Register New Staff</h3>
              <RFIDInput
                mode="EMPLOYEE_REGISTRATION"
                label="Scan staff RFID card on reader"
                onScan={handleEmployeeScan}
              />
              <form onSubmit={handleRegisterEmployee}>
                <div className="form-group">
                  <label>Employee ID *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={empForm.employee_id}
                    onChange={e => setEmpForm({ ...empForm, employee_id: e.target.value })}
                    placeholder="e.g. EMP003"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={empForm.name}
                    onChange={e => setEmpForm({ ...empForm, name: e.target.value })}
                    placeholder="e.g. Anjali Sharma"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Store Role *</label>
                  <select
                    className="form-control"
                    value={empForm.role}
                    onChange={e => setEmpForm({ ...empForm, role: e.target.value })}
                  >
                    <option value="SALESPERSON">Salesperson</option>
                    <option value="MANAGER">Manager</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Assigned Section</label>
                  <input
                    type="text"
                    className="form-control"
                    value={empForm.section}
                    onChange={e => setEmpForm({ ...empForm, section: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Card RFID UID</label>
                  <input
                    type="text"
                    className="form-control"
                    value={empForm.rfid_uid}
                    onChange={e => setEmpForm({ ...empForm, rfid_uid: e.target.value })}
                    placeholder="Scan or enter UID"
                  />
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                  Register Employee
                </button>
              </form>
            </div>

            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Active Staff Directory</h3>
              <div className="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Role</th>
                      <th>RFID UID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map(emp => (
                      <tr key={emp.employee_id}>
                        <td><strong>{emp.employee_id}</strong></td>
                        <td>{emp.name}</td>
                        <td><span className="badge badge-assigned">{emp.role}</span></td>
                        <td><code>{emp.rfid_uid || 'None'}</code></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: PRODUCT REGISTRATION */}
        {activeTab === 'products' && (
          <div className="grid-2">
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Register Jewellery Item</h3>
              <RFIDInput
                mode="PRODUCT_REGISTRATION"
                label="Scan item RFID tag on reader"
                onScan={handleProductScan}
              />
              <form onSubmit={handleRegisterProduct}>
                <div className="form-group">
                  <label>Product ID *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={prodForm.product_id}
                    onChange={e => setProdForm({ ...prodForm, product_id: e.target.value })}
                    placeholder="e.g. JWL001"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Product Name *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={prodForm.product_name}
                    onChange={e => setProdForm({ ...prodForm, product_name: e.target.value })}
                    placeholder="e.g. 22K Gold Solitaire Ring"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <input
                    type="text"
                    className="form-control"
                    value={prodForm.category}
                    onChange={e => setProdForm({ ...prodForm, category: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Weight</label>
                  <input
                    type="text"
                    className="form-control"
                    value={prodForm.weight}
                    onChange={e => setProdForm({ ...prodForm, weight: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Price (₹)</label>
                  <input
                    type="number"
                    className="form-control"
                    value={prodForm.price}
                    onChange={e => setProdForm({ ...prodForm, price: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Assigned Case *</label>
                  <select
                    className="form-control"
                    value={prodForm.case_id}
                    onChange={e => setProdForm({ ...prodForm, case_id: e.target.value })}
                  >
                    <option value="CASE-01">CASE-01 (Functional)</option>
                    <option value="CASE-02">CASE-02 (Functional)</option>
                    <option value="CASE-03">CASE-03 (Functional)</option>
                    <option value="CASE-04" disabled>CASE-04 (Inactive/Future)</option>
                    <option value="CASE-05" disabled>CASE-05 (Inactive/Future)</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>RFID Tag UID *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={prodForm.rfid_uid}
                    onChange={e => setProdForm({ ...prodForm, rfid_uid: e.target.value })}
                    placeholder="Scan or enter tag UID"
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                  Register Item & Bind RFID
                </button>
              </form>
            </div>

            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Inventory Items</h3>
              <div className="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Case</th>
                      <th>RFID</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map(p => (
                      <tr key={p.product_id}>
                        <td>
                          <strong>{p.product_id}</strong>
                          <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{p.product_name}</div>
                        </td>
                        <td>{p.case_id}</td>
                        <td><code>{p.rfid_uid || 'Released'}</code></td>
                        <td>
                          <span className={`badge badge-${p.current_status.toLowerCase()}`}>
                            {p.current_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: BILLING */}
        {activeTab === 'billing' && (
          <div className="grid-2">
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Scan Jewellery for Sale</h3>
              <RFIDInput
                mode="BILLING"
                label="Scan item RFID tag to initiate billing (Must be IN_HANDLING)"
                onScan={handleBillingScan}
              />
              {billingProduct ? (
                <div style={{ marginTop: '1.5rem', background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
                  <h4 style={{ color: '#1e3a8a', marginBottom: '0.75rem' }}>Active Billing Session</h4>
                  <p><strong>Item:</strong> {billingProduct.product_id} - {billingProduct.product_name}</p>
                  <p><strong>Category:</strong> {billingProduct.category} | <strong>Weight:</strong> {billingProduct.weight}</p>
                  <p><strong>Price:</strong> ₹{billingProduct.price}</p>
                  <p><strong>Handler:</strong> {billingProduct.handler?.name || billingProduct.current_handler_employee_id || 'None'}</p>

                  <div style={{ marginTop: '1rem' }}>
                    <div className="form-group">
                      <label>Customer Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={customerForm.name}
                        onChange={e => setCustomerForm({ ...customerForm, name: e.target.value })}
                        placeholder="e.g. Ramesh Kumar"
                      />
                    </div>
                    <div className="form-group">
                      <label>Customer Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        value={customerForm.phone}
                        onChange={e => setCustomerForm({ ...customerForm, phone: e.target.value })}
                        placeholder="e.g. 9876543210"
                      />
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                      <button className="btn btn-danger" style={{ flex: 1 }} onClick={handleCancelBilling}>
                        Cancel Billing
                      </button>
                      <button className="btn btn-success" style={{ flex: 2 }} onClick={handleCompleteSale}>
                        Complete Sale & Release Tag
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <p style={{ color: '#64748b', marginTop: '1rem' }}>No item currently loaded in billing counter.</p>
              )}
            </div>

            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>Completed Sales History</h3>
              <SalesList />
            </div>
          </div>
        )}

        {/* TAB 4: CASES */}
        {activeTab === 'cases' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Store Display Cases (3 Functional, 2 Future)</h3>
            <div className="grid-3">
              {cases.map(c => (
                <div key={c.case_id} style={{
                  padding: '1.25rem',
                  borderRadius: '8px',
                  border: `2px solid ${c.functional ? (c.current_status === 'ASSIGNED' ? '#2563eb' : '#16a34a') : '#cbd5e1'}`,
                  background: c.functional ? '#ffffff' : '#f1f5f9'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4>{c.case_id}</h4>
                    <span className={`badge ${c.functional ? 'badge-available' : 'badge-sold'}`}>
                      {c.functional ? 'Functional' : 'Future/Inactive'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>{c.name}</p>
                  <div style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
                    <p><strong>Status:</strong> {c.current_status}</p>
                    <p><strong>Assigned To:</strong> {c.current_assignment?.employee_name || 'None'}</p>
                    <p><strong>Items:</strong> {c.product_count} registered</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: RFID REGISTRY & REUSE */}
        {activeTab === 'rfids' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Central RFID Registry & Lifecycle Tracking</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>UID</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Current Assignment</th>
                    <th>Historical Lifecycle</th>
                  </tr>
                </thead>
                <tbody>
                  {rfids.map(r => (
                    <tr key={r.uid}>
                      <td><code>{r.uid}</code></td>
                      <td>{r.rfid_type}</td>
                      <td>
                        <span className={`badge badge-${r.status.toLowerCase()}`}>
                          {r.status}
                        </span>
                      </td>
                      <td>{r.current_assignment || 'None (Released)'}</td>
                      <td>
                        {r.assignment_history?.length > 0 ? (
                          <div style={{ fontSize: '0.8rem', color: '#475569' }}>
                            {r.assignment_history.map(h => (
                              <div key={h.id}>
                                • {h.product_id} ({h.product_name}) - [{h.status}]
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span style={{ color: '#94a3b8' }}>-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 6: ACTIVITY LOGS */}
        {activeTab === 'logs' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>System Audit Trail</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Role</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(l => (
                    <tr key={l.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>{l.timestamp}</td>
                      <td><strong>{l.action}</strong></td>
                      <td>{l.role}</td>
                      <td>{l.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal for RFID Tag Reuse */}
      {reassignModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ color: '#7c3aed', marginBottom: '1rem' }}>RFID AVAILABLE FOR REUSE</h3>
            <p><strong>Scanned RFID:</strong> <code>{reassignModal.uid}</code></p>
            {reassignModal.prev && (
              <div style={{ margin: '1rem 0', padding: '0.75rem', background: '#f8fafc', borderRadius: '6px' }}>
                <p><strong>Previous Product:</strong> {reassignModal.prev.product_id} ({reassignModal.prev.product_name})</p>
                <p><strong>Previous Status:</strong> SOLD</p>
                <p><strong>Released At:</strong> {reassignModal.prev.released_at}</p>
              </div>
            )}
            <p style={{ marginTop: '0.5rem', color: '#334155' }}>
              Assign this released RFID tag to new product <strong>{reassignModal.formData.product_id}</strong>?
            </p>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setReassignModal(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" style={{ flex: 1, background: '#7c3aed' }} onClick={confirmReassign}>
                Confirm Reassign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SalesList() {
  const [sales, setSales] = useState([]);
  useEffect(() => {
    api.getSales().then(setSales).catch(console.error);
  }, []);

  return (
    <div className="table-responsive">
      <table>
        <thead>
          <tr>
            <th>Bill #</th>
            <th>Item</th>
            <th>Customer</th>
            <th>Amount</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {sales.map(s => (
            <tr key={s.id}>
              <td><strong>{s.bill_number}</strong></td>
              <td>{s.product_id} ({s.product_name})</td>
              <td>{s.customer_name}</td>
              <td>₹{s.amount}</td>
              <td style={{ fontSize: '0.85rem' }}>{s.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
