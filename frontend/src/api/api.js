const BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await res.json();
  if (!res.ok && !data.success) {
    throw data;
  }
  return data;
}

export const api = {
  // Auth
  adminLogin: (password) => request('/auth/admin-login', { method: 'POST', body: { password } }),
  rfidLogin: (rfid_uid, expected_role) => request('/auth/rfid-login', { method: 'POST', body: { rfid_uid, expected_role } }),
  logout: (employee_id) => request('/auth/logout', { method: 'POST', body: { employee_id } }),

  // Admin
  getEmployees: () => request('/admin/employees'),
  registerEmployee: (data) => request('/admin/register-employee', { method: 'POST', body: data }),
  getProducts: () => request('/admin/products'),
  registerProduct: (data) => request('/admin/register-product', { method: 'POST', body: data }),
  reassignTag: (data) => request('/admin/reassign-tag', { method: 'POST', body: data }),
  getCases: () => request('/admin/cases'),
  getRfidRegistry: () => request('/admin/rfid-registry'),
  checkRfid: (rfid_uid) => request('/admin/rfid-check', { method: 'POST', body: { rfid_uid } }),
  getActivityLogs: (limit = 100) => request(`/admin/activity-logs?limit=${limit}`),

  // Salesperson
  getDashboard: (employee_id) => request(`/salesperson/dashboard?employee_id=${employee_id}`),
  scanItem: (rfid_uid, employee_id, case_id) => request('/salesperson/scan-item', { method: 'POST', body: { rfid_uid, employee_id, case_id } }),

  // Billing
  billingScan: (rfid_uid) => request('/billing/scan', { method: 'POST', body: { rfid_uid } }),
  cancelBilling: (product_id) => request('/billing/cancel', { method: 'POST', body: { product_id } }),
  completeSale: (data) => request('/billing/complete', { method: 'POST', body: data }),
  getSales: () => request('/billing/sales'),

  // Manager
  getManagerDashboard: () => request('/manager/dashboard'),
  getManagerActivityLogs: (limit = 100) => request(`/manager/activity-logs?limit=${limit}`),
  getCaseHistory: () => request('/manager/case-history'),
  getProductHistory: () => request('/manager/product-history'),
  getManagerSales: () => request('/manager/sales'),
  getRfidHistory: () => request('/manager/rfid-history'),
  getManagerProducts: () => request('/manager/products'),

  // Health
  health: () => request('/health'),
};
