import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import RFIDInput from '../../components/RFIDInput';
import { api } from '../../api/api';

export default function SalespersonLogin() {
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  const handleScan = async (uid) => {
    setErrorMsg('');
    try {
      const res = await api.rfidLogin(uid, 'SALESPERSON');
      if (res.success) {
        // Save to local storage for persistence across views
        localStorage.setItem('salesperson_auth', JSON.stringify(res));
        navigate('/salesperson/dashboard');
        return { feedback: { type: 'success', text: `Welcome ${res.name}! Allocated ${res.case_id}` } };
      }
    } catch (err) {
      setErrorMsg(err.error || 'Authentication failed.');
      throw err;
    }
  };

  return (
    <div>
      <Navbar title="Salesperson Login" backTo="/" />

      <div className="container" style={{ maxWidth: '550px', marginTop: '3rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🪪</div>
          <h2 style={{ marginBottom: '0.5rem' }}>Salesperson Identification</h2>
          <p style={{ color: '#64748b', marginBottom: '2rem', fontSize: '0.95rem' }}>
            Scan your employee RFID badge on the USB reader to authenticate and be automatically allocated an active jewellery case.
          </p>

          <RFIDInput
            mode="SALESPERSON_LOGIN"
            label="Waiting for Salesperson Badge scan..."
            onScan={handleScan}
          />

          {errorMsg && (
            <div className="rfid-feedback rfid-feedback-error" style={{ textAlign: 'left', marginTop: '1rem' }}>
              <strong>Error: </strong> {errorMsg}
            </div>
          )}

          <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8fafc', borderRadius: '6px', textAlign: 'left', fontSize: '0.85rem', color: '#64748b' }}>
            <p><strong>Demo Salesperson Badges:</strong></p>
            <p>• Rahul: <code>EMP_RFID_001</code></p>
            <p>• Priya: <code>EMP_RFID_002</code></p>
          </div>
        </div>
      </div>
    </div>
  );
}
