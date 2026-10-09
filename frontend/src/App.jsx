import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home/Home';
import AdminPortal from './pages/Admin/AdminPortal';
import SalespersonLogin from './pages/Salesperson/SalespersonLogin';
import SalespersonDashboard from './pages/Salesperson/SalespersonDashboard';
import ManagerLogin from './pages/Manager/ManagerLogin';
import ManagerDashboard from './pages/Manager/ManagerDashboard';
import './index.css';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        
        {/* Admin Routes */}
        <Route path="/admin" element={<AdminPortal />} />
        
        {/* Salesperson Routes */}
        <Route path="/salesperson/login" element={<SalespersonLogin />} />
        <Route path="/salesperson/dashboard" element={<SalespersonDashboard />} />
        
        {/* Manager Routes */}
        <Route path="/manager/login" element={<ManagerLogin />} />
        <Route path="/manager/dashboard" element={<ManagerDashboard />} />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
