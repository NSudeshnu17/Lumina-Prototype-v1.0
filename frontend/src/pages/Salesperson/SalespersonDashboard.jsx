import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import RFIDInput from '../../components/RFIDInput';
import { api } from '../../api/api';

export default function SalespersonDashboard() {
  const [auth, setAuth] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const navigate = useNavigate();

  const loadData = async (empId) => {
    try {
      const data = await api.getDashboard(empId);
      setDashboardData(data);
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem('salesperson_auth');
    if (!stored) {
      navigate('/salesperson/login');
      return;
    }
    const parsed = JSON.parse(stored);
    setAuth(parsed);
    loadData(parsed.employee_id);
  }, [navigate]);

  const handleItemScan = async (uid) => {
    setErrorMsg('');
    setSuccessMsg('');
    if (!auth || !dashboardData) return;

    try {
      const res = await api.scanItem(uid, auth.employee_id, dashboardData.case_id);
      if (res.action === 'ITEM_REMOVED') {
        setSuccessMsg(`ITEM REMOVED: ${res.product_name} (${res.product}) is now IN_HANDLING for customer display.`);
      } else if (res.action === 'ITEM_RETURNED') {
        setSuccessMsg(`ITEM RETURNED: ${res.product_name} (${res.product}) safely returned to ${dashboardData.case_id}.`);
      }
      loadData(auth.employee_id);
      return { feedback: { type: 'success', text: `Action: ${res.action} for ${res.product}` } };
    } catch (err) {
      if (err.code === 'WRONG_CASE') {
        setErrorMsg(`ITEM DOES NOT BELONG TO YOUR CASE: ${err.product_id} belongs to ${err.product_case}, but you are assigned to ${err.your_case}.`);
      } else if (err.code === 'HANDLED_BY_OTHER') {
        setErrorMsg(`ITEM ALREADY IN HANDLING: ${err.product_id} is currently handled by ${err.handler_name} (${err.handler}).`);
      } else {
        setErrorMsg(err.error || 'Failed to process item scan.');
      }
      throw err;
    }
  };

  const handleLogout = async () => {
    setErrorMsg('');
    try {
      await api.logout(auth?.employee_id);
      localStorage.removeItem('salesperson_auth');
      navigate('/');
    } catch (err) {
      if (err.items) {
        setErrorMsg(`LOGOUT BLOCKED: You have ${err.items.length} unresolved item(s) in handling/billing. Please return them first.`);
      } else {
        setErrorMsg(err.error || 'Logout failed.');
      }
    }
  };

  if (loading) return <div className="container" style={{ marginTop: '3rem' }}>Loading session...</div>;

  return (
    <div>
      <Navbar title={`Sales Desk — ${auth?.name || 'Staff'}`} />

      <div className="container">
        {/* Top Header Card */}
        <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ color: '#0f172a' }}>Welcome, {auth?.name}</h2>
            <div style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '0.25rem' }}>
              Employee ID: <strong>{auth?.employee_id}</strong> | Allocated Case: <strong style={{ color: '#2563eb' }}>{dashboardData?.case_id}</strong>
            </div>
          </div>
          <button className="btn btn-danger" onClick={handleLogout}>
            Release Case & Logout
          </button>
        </div>

        {/* Global Feedback */}
        {errorMsg && (
          <div className="rfid-feedback rfid-feedback-error" style={{ marginBottom: '1.5rem' }}>
            <strong>Alert: </strong> {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="rfid-feedback rfid-feedback-success" style={{ marginBottom: '1.5rem' }}>
            <strong>Success: </strong> {successMsg}
          </div>
        )}

        {/* Quick Stats Grid */}
        <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-lbl">Case Items</span>
            <span className="stat-val">{dashboardData?.stats?.total || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-lbl">Available</span>
            <span className="stat-val" style={{ color: '#16a34a' }}>{dashboardData?.stats?.available || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-lbl">In Handling</span>
            <span className="stat-val" style={{ color: '#d97706' }}>{dashboardData?.stats?.in_handling || 0}</span>
          </div>
        </div>

        {/* Interactive RFID Handling Area */}
        <div className="grid-2">
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Physical Item Handling Scanner</h3>
            <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Scan an item RFID to <strong>REMOVE</strong> it from {dashboardData?.case_id}. Scan it again to <strong>RETURN</strong> it.
            </p>

            <RFIDInput
              mode="ITEM_HANDLING"
              label={`● ${dashboardData?.case_id} ITEM HANDLING — Scan jewellery RFID...`}
              onScan={handleItemScan}
            />

            <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>Current Handling Workflow</h4>
            <div style={{ fontSize: '0.85rem', color: '#475569', background: '#f8fafc', padding: '1rem', borderRadius: '6px' }}>
              <p>• <strong>Scan 1:</strong> AVAILABLE → IN_HANDLING (Item taken out for customer)</p>
              <p>• <strong>Scan 2:</strong> IN_HANDLING → AVAILABLE (Item returned safely to case)</p>
              <p>• <strong>To Sell:</strong> Handover to Admin Billing while IN_HANDLING</p>
            </div>
          </div>

          {/* Case Inventory Table */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>{dashboardData?.case_id} Registered Inventory</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>RFID UID</th>
                    <th>Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData?.products?.map(p => (
                    <tr key={p.product_id}>
                      <td>
                        <strong>{p.product_id}</strong>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{p.product_name}</div>
                      </td>
                      <td><code>{p.rfid_uid || 'None'}</code></td>
                      <td>₹{p.price}</td>
                      <td>
                        <span className={`badge badge-${p.current_status.toLowerCase()}`}>
                          {p.current_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {dashboardData?.products?.length === 0 && (
                    <tr>
                      <td colSpan="4" style={{ textAlign: 'center', color: '#94a3b8' }}>
                        No products currently assigned to this case.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Recent Session Logs */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Your Recent Activity Trail</h3>
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Action</th>
                  <th>Product</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData?.recent_activity?.map(l => (
                  <tr key={l.id}>
                    <td style={{ whiteSpace: 'nowrap' }}>{l.timestamp}</td>
                    <td><strong>{l.action}</strong></td>
                    <td>{l.product_id || '-'}</td>
                    <td>{l.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
