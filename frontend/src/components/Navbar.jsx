import { Link, useNavigate } from 'react-router-dom';

export default function Navbar({ title, backTo }) {
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <div className="navbar-left">
        {backTo && (
          <button className="nav-back-btn" onClick={() => navigate(backTo)}>
            ← Back
          </button>
        )}
        <Link to="/" className="nav-brand">LUMINA RFID</Link>
      </div>
      <div className="navbar-center">
        <h1 className="nav-title">{title}</h1>
      </div>
      <div className="navbar-right"></div>
    </nav>
  );
}
