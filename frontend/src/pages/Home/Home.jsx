import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div>
      <header className="navbar">
        <div className="navbar-left">
          <span className="nav-brand">LUMINA RFID</span>
          <span className="nav-title">Smart Jewellery Handling System</span>
        </div>
      </header>

      <main className="container" style={{ marginTop: '4rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.75rem' }}>
            Store Operations Portal
          </h2>
          <p style={{ color: '#64748b', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
            Select your operational role module to begin RFID tracking, handling, or store auditing.
          </p>
        </div>

        <div className="grid-3">
          {/* Card 1: Admin */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderTop: '4px solid #1e3a8a' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.75rem' }}>⚙️</span>
                <h3 style={{ fontSize: '1.4rem', color: '#0f172a' }}>Admin Module</h3>
              </div>
              <p style={{ color: '#64748b', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                Configure store staff, register jewellery products, manage cases, process sales billing, and view audit activity logs.
              </p>
              <ul style={{ listStyle: 'none', color: '#475569', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                <li style={{ marginBottom: '0.5rem' }}>✓ Employee & Product Registration</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ RFID Tag Reassignment & Status</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ Integrated Store Billing</li>
              </ul>
            </div>
            <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => navigate('/admin')}>
              Enter Admin Portal →
            </button>
          </div>

          {/* Card 2: Salesperson */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderTop: '4px solid #059669' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.75rem' }}>🏷️</span>
                <h3 style={{ fontSize: '1.4rem', color: '#0f172a' }}>Salesperson</h3>
              </div>
              <p style={{ color: '#64748b', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                Scan employee card for automatic case allocation, remove items for customer viewing, and return items safely.
              </p>
              <ul style={{ listStyle: 'none', color: '#475569', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                <li style={{ marginBottom: '0.5rem' }}>✓ RFID Fast Login</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ Automatic Priority Case Allocation</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ Single-Reader Item Handling & Return</li>
              </ul>
            </div>
            <button className="btn btn-success" style={{ width: '100%', background: '#059669' }} onClick={() => navigate('/salesperson/login')}>
              Salesperson Login →
            </button>
          </div>

          {/* Card 3: Manager */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderTop: '4px solid #0891b2' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.75rem' }}>📊</span>
                <h3 style={{ fontSize: '1.4rem', color: '#0f172a' }}>Store Manager</h3>
              </div>
              <p style={{ color: '#64748b', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                Real-time dashboard for full store visibility, active case allocations, item movement history, and unresolved item alerts.
              </p>
              <ul style={{ listStyle: 'none', color: '#475569', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                <li style={{ marginBottom: '0.5rem' }}>✓ Real-time 5-Case Store View</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ Complete Timestamp Audit Trail</li>
                <li style={{ marginBottom: '0.5rem' }}>✓ Product Movement & Sales History</li>
              </ul>
            </div>
            <button className="btn btn-primary" style={{ width: '100%', background: '#0891b2' }} onClick={() => navigate('/manager/login')}>
              Manager Portal →
            </button>
          </div>
        </div>

        <div style={{ marginTop: '3rem', textAlign: 'center', color: '#94a3b8', fontSize: '0.85rem' }}>
          Phase-1 Prototype • 1 USB RFID Reader • Local SQLite Architecture
        </div>
      </main>
    </div>
  );
}
