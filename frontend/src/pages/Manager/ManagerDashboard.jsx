import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import { api } from '../../api/api';

export default function ManagerDashboard() {
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [caseHistory, setCaseHistory] = useState([]);
  const [prodHistory, setProdHistory] = useState([]);
  const [sales, setSales] = useState([]);
  const [rfids, setRfids] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadAll = async () => {
    try {
      setLoading(true);
      const [dash, ch, ph, s, r, l] = await Promise.all([
        api.getManagerDashboard(),
        api.getCaseHistory(),
        api.getProductHistory(),
        api.getManagerSales(),
        api.getRfidHistory(),
        api.getManagerActivityLogs(100)
      ]);
      setData(dash);
      setCaseHistory(ch);
      setProdHistory(ph);
      setSales(s);
      setRfids(r);
      setLogs(l);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('manager_auth');
    navigate('/');
  };

  if (loading) return <div className="container" style={{ marginTop: '3rem' }}>Loading Manager Console...</div>;

  const stats = data?.stats || {};
  const cases = data?.cases || [];

  return (
    <div>
      <Navbar title="Store Operations & Audit Oversight" />

      <div className="container">
        {/* Header Bar */}
        <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2>Manager Oversight Console</h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Real-time monitoring of display cases, allocations, and compliance audit trail</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-secondary" onClick={loadAll}>Refresh</button>
            <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
          </div>
        </div>

        {/* Top Operational Metrics */}
        <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-lbl">Active Staff Logged In</span>
            <span className="stat-val" style={{ color: '#2563eb' }}>{stats.logged_in_employees || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-lbl">Unresolved Items (Handling/Billing)</span>
            <span className="stat-val" style={{ color: stats.unresolved_items > 0 ? '#dc2626' : '#16a34a' }}>
              {stats.unresolved_items || 0}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-lbl">Total Completed Sales</span>
            <span className="stat-val" style={{ color: '#16a34a' }}>{stats.total_sales || 0}</span>
          </div>
        </div>

        {/* Detailed Metrics Subgrid */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>TOTAL CASES</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{stats.total_cases}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>FUNCTIONAL CASES</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#2563eb' }}>{stats.functional_cases}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>ASSIGNED CASES</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#d97706' }}>{stats.assigned_cases}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>AVAILABLE CASES</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#16a34a' }}>{stats.available_cases}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>AVAILABLE ITEMS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#16a34a' }}>{stats.available_products}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>SOLD ITEMS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#475569' }}>{stats.sold_products}</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', overflowX: 'auto' }}>
          {[
            { id: 'overview', label: 'Case Status View' },
            { id: 'case_history', label: 'Case Allocation History' },
            { id: 'product_history', label: 'Product State History' },
            { id: 'sales', label: 'Sales Records' },
            { id: 'rfid_lifecycle', label: 'RFID Reuse History' },
            { id: 'audit_logs', label: 'Full System Audit Trail' },
          ].map(tab => (
            <button
              key={tab.id}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: ALL 5 CASES LIVE VIEW */}
        {activeTab === 'overview' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Display Case Inventory & Staff Allocation</h3>
            <div className="grid-3">
              {cases.map(c => (
                <div key={c.case_id} style={{
                  padding: '1.25rem',
                  borderRadius: '8px',
                  border: `2px solid ${c.functional ? (c.current_status === 'ASSIGNED' ? '#2563eb' : '#16a34a') : '#cbd5e1'}`,
                  background: c.functional ? '#ffffff' : '#f8fafc'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4>{c.case_id}</h4>
                    <span className={`badge ${c.functional ? 'badge-available' : 'badge-sold'}`}>
                      {c.functional ? 'Functional' : 'Inactive/Future'}
                    </span>
                  </div>
                  <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '0.25rem' }}>{c.name}</p>

                  <div style={{ marginTop: '1rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
                    <div><strong>Status:</strong> <span className={`badge badge-${c.current_status.toLowerCase()}`}>{c.current_status}</span></div>
                    <div><strong>Active Handler:</strong> {c.current_assignment?.employee_name || 'None (Unoccupied)'}</div>
                    <div><strong>Assigned Since:</strong> {c.current_assignment?.assigned_at || '-'}</div>
                    <div><strong>Items in Case:</strong> {c.product_count}</div>
                  </div>

                  {c.products?.length > 0 && (
                    <div style={{ marginTop: '1rem', borderTop: '1px solid #e2e8f0', paddingTop: '0.5rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>REGISTERED PRODUCTS:</span>
                      {c.products.map(p => (
                        <div key={p.product_id} style={{ fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
                          <span>{p.product_id} ({p.product_name})</span>
                          <span className={`badge badge-${p.current_status.toLowerCase()}`}>{p.current_status}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 2: CASE ALLOCATION HISTORY */}
        {activeTab === 'case_history' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Historical Case Allocations (Preserved Logs)</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Staff Name</th>
                    <th>Employee ID</th>
                    <th>Assigned At</th>
                    <th>Released At</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {caseHistory.map(ch => (
                    <tr key={ch.id}>
                      <td><strong>{ch.case_id}</strong></td>
                      <td>{ch.employee_name}</td>
                      <td>{ch.employee_id}</td>
                      <td>{ch.assigned_at}</td>
                      <td>{ch.released_at || 'Currently Active'}</td>
                      <td>
                        <span className={`badge ${ch.status === 'ACTIVE' ? 'badge-assigned' : 'badge-sold'}`}>
                          {ch.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: PRODUCT STATE HISTORY */}
        {activeTab === 'product_history' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Lifecycle State Transitions (Audit Trail)</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Product</th>
                    <th>Transition</th>
                    <th>Handler / Staff</th>
                    <th>Case</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {prodHistory.map(ph => (
                    <tr key={ph.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>{ph.timestamp}</td>
                      <td><strong>{ph.product_id}</strong> <span style={{ color: '#64748b' }}>({ph.product_name})</span></td>
                      <td>
                        <code>{ph.old_state || 'REGISTER'}</code> → <strong style={{ color: '#2563eb' }}>{ph.new_state}</strong>
                      </td>
                      <td>{ph.employee_id || 'System'}</td>
                      <td>{ph.case_id || '-'}</td>
                      <td>{ph.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: SALES */}
        {activeTab === 'sales' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Completed Sales Invoices</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Bill Number</th>
                    <th>Product</th>
                    <th>Customer Name</th>
                    <th>Phone</th>
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
                      <td>{s.customer_phone}</td>
                      <td>₹{s.amount}</td>
                      <td>{s.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: RFID LIFECYCLE & REUSE */}
        {activeTab === 'rfid_lifecycle' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Physical RFID Tag Reuse Chain</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>RFID UID</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Current Assignment</th>
                    <th>Historical Assignments</th>
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
                          <div>
                            {r.assignment_history.map(h => (
                              <div key={h.id} style={{ fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                                • <strong>{h.product_id}</strong> ({h.product_name}) | Assigned: {h.assigned_at} | Released: {h.released_at || 'Active'}
                              </div>
                            ))}
                          </div>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 6: AUDIT TRAIL */}
        {activeTab === 'audit_logs' && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>System Audit Logs</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Role</th>
                    <th>Actor</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(l => (
                    <tr key={l.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>{l.timestamp}</td>
                      <td><strong>{l.action}</strong></td>
                      <td>{l.role}</td>
                      <td>{l.employee_id || '-'}</td>
                      <td>{l.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
