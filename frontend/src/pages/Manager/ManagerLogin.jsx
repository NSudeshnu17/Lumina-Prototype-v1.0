import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import RFIDInput from '../../components/RFIDInput';
import { api } from '../../api/api';

export default function ManagerLogin() {
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  const handleScan = async (uid) => {
    setErrorMsg('');
    try {
      const res = await api.rfidLogin(uid, 'MANAGER');
      if (res.success) {
        localStorage.setItem('manager_auth', JSON.stringify(res));
        navigate('/manager/dashboard');
        return { feedback: { type: 'success', text: `Welcome Manager ${res.name}!` } };
      }
    } catch (err) {
      setErrorMsg(err.error || 'Manager authentication failed.');
      throw err;
    }
  };

  return (
    <div>
      <Navbar title="Manager Login" backTo="/" />

      <div className="container" style={{ maxWidth: '550px', marginTop: '3rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🛡️</div>
          <h2 style={{ marginBottom: '0.5rem' }}>Manager Identification</h2>
          <p style={{ color: '#64748b', marginBottom: '2rem', fontSize: '0.95rem' }}>
            Scan authorized Manager RFID badge to access store-wide oversight, case allocations, and full audit logs.
          </p>

          <RFIDInput
            mode="MANAGER_LOGIN"
            label="Waiting for Manager Badge scan..."
            onScan={handleScan}
          />

          {errorMsg && (
            <div className="rfid-feedback rfid-feedback-error" style={{ textAlign: 'left', marginTop: '1rem' }}>
              <strong>Error: </strong> {errorMsg}
            </div>
          )}

          <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8fafc', borderRadius: '6px', textAlign: 'left', fontSize: '0.85rem', color: '#64748b' }}>
            <p><strong>Demo Manager Badge:</strong></p>
            <p>• Manager: <code>MGR_RFID_001</code></p>
          </div>
        </div>
      </div>
    </div>
  );
}
