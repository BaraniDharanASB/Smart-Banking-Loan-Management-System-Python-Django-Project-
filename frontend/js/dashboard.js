// Smart Banking & Loan Management System - Dashboard JS

document.addEventListener('DOMContentLoaded', async () => {
  const profile = await loadUserProfile();
  if (!profile) return;

  renderNavbar();

  const role = profile.role;
  const container = document.getElementById('dashboard-content');
  if (!container) return;

  if (role === 'CUSTOMER') {
    await renderCustomerDashboard(container, profile);
  } else if (role === 'EMPLOYEE') {
    await renderEmployeeDashboard(container);
  } else if (role === 'ADMIN') {
    await renderAdminDashboard(container);
  }
});

// Render Customer Dashboard
async function renderCustomerDashboard(container, profile) {
  const response = await fetchWithAuth('/dashboard/customer/');
  if (!response) return;

  let data = {};
  if (response.ok) {
    data = await response.json();
  }

  const recentTx = data.recent_transactions || [];

  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-title">Welcome, ${data.customer_name || profile.username}!</h1>
      <button onclick="openProfileModal()" class="btn btn-sm btn-secondary">Manage Profile</button>
    </div>

    <div class="grid grid-cols-4" style="margin-bottom: 2rem;">
      <div class="card">
        <div class="card-title">Total Active Balance</div>
        <div class="card-value">$${parseFloat(data.total_balance || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
      <div class="card">
        <div class="card-title">Savings Balance</div>
        <div class="card-value">$${parseFloat(data.savings_account_balance || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
      <div class="card">
        <div class="card-title">Current Balance</div>
        <div class="card-value">$${parseFloat(data.current_account_balance || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
      <div class="card">
        <div class="card-title">Outstanding Loans</div>
        <div class="card-value" style="color: var(--danger-color);">$${parseFloat(data.total_outstanding_loan_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
    </div>

    <div class="grid grid-cols-2" style="margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem;">Banking Summary</h3>
        <p><strong>Bank Accounts:</strong> ${data.total_bank_accounts || 0}</p>
        <p><strong>Total Transactions:</strong> ${data.total_transactions || 0}</p>
        <div style="margin-top: 1rem;">
          <a href="accounts.html" class="btn btn-sm btn-primary">Go to Accounts</a>
        </div>
      </div>
      <div class="card">
        <h3 style="margin-bottom: 1rem;">Loans Summary</h3>
        <p><strong>Total Loans:</strong> ${data.total_loans || 0}</p>
        <p><strong>Pending:</strong> ${data.pending_loans || 0} | <strong>Approved:</strong> ${data.approved_loans || 0}</p>
        <p><strong>Rejected:</strong> ${data.rejected_loans || 0} | <strong>Closed:</strong> ${data.closed_loans || 0}</p>
        <div style="margin-top: 1rem;">
          <a href="loans.html" class="btn btn-sm btn-primary">Apply / View Loans</a>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-bottom: 1rem;">Recent Transactions (Latest 5)</h3>
      ${recentTx.length === 0 ? '<p style="color: var(--text-muted);">No recent transactions found.</p>' : `
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Txn ID</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              ${recentTx.map(tx => `
                <tr>
                  <td><code>${tx.transaction_id}</code></td>
                  <td><strong>${tx.transaction_type}</strong></td>
                  <td>$${parseFloat(tx.amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td><span class="badge badge-${tx.status.toLowerCase()}">${tx.status}</span></td>
                  <td>${new Date(tx.transaction_date).toLocaleString()}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `}
    </div>
  `;
}

// Render Employee Dashboard
async function renderEmployeeDashboard(container) {
  const response = await fetchWithAuth('/dashboard/employee/');
  if (!response || !response.ok) return;

  const data = await response.json();

  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-title">Employee Portal Dashboard</h1>
    </div>

    <div class="grid grid-cols-4" style="margin-bottom: 2rem;">
      <div class="card">
        <div class="card-title">Total Customers</div>
        <div class="card-value">${data.total_customers}</div>
      </div>
      <div class="card">
        <div class="card-title">Active Bank Accounts</div>
        <div class="card-value">${data.total_active_accounts} / ${data.total_bank_accounts}</div>
      </div>
      <div class="card">
        <div class="card-title">Pending Loans</div>
        <div class="card-value" style="color: var(--warning-color);">${data.pending_loans}</div>
      </div>
      <div class="card">
        <div class="card-title">Total Loan Portfolio</div>
        <div class="card-value">$${parseFloat(data.total_loan_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
    </div>

    <div class="grid grid-cols-2">
      <div class="card">
        <h3 style="margin-bottom: 1rem;">Loan Processing Overview</h3>
        <p><strong>Approved Loans:</strong> ${data.approved_loans}</p>
        <p><strong>Rejected Loans:</strong> ${data.rejected_loans}</p>
        <p><strong>Closed Loans:</strong> ${data.closed_loans}</p>
        <div style="margin-top: 1.5rem;">
          <a href="loans.html" class="btn btn-primary">Process Pending Loans</a>
        </div>
      </div>
      <div class="card">
        <h3 style="margin-bottom: 1rem;">System Overview</h3>
        <p><strong>Total System Transactions:</strong> ${data.total_transactions}</p>
        <p><strong>Total Accounts:</strong> ${data.total_bank_accounts}</p>
        <div style="margin-top: 1.5rem;">
          <a href="transactions.html" class="btn btn-secondary">View System Transactions</a>
        </div>
      </div>
    </div>
  `;
}

// Render Admin Dashboard
async function renderAdminDashboard(container) {
  const response = await fetchWithAuth('/dashboard/admin/');
  if (!response || !response.ok) return;

  const data = await response.json();

  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-title">Admin Management Dashboard</h1>
    </div>

    <div class="grid grid-cols-4" style="margin-bottom: 2rem;">
      <div class="card">
        <div class="card-title">Total Employees</div>
        <div class="card-value">${data.total_employees}</div>
      </div>
      <div class="card">
        <div class="card-title">Total Customers</div>
        <div class="card-value">${data.total_customers}</div>
      </div>
      <div class="card">
        <div class="card-title">Active / Blocked Accounts</div>
        <div class="card-value">${data.total_active_accounts} / ${data.total_blocked_accounts}</div>
      </div>
      <div class="card">
        <div class="card-title">Total Loan Portfolio</div>
        <div class="card-value">$${parseFloat(data.total_loan_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
      </div>
    </div>

    <div class="grid grid-cols-2">
      <div class="card">
        <h3 style="margin-bottom: 1rem;">System Volume Totals</h3>
        <p><strong>Total Deposits:</strong> $${parseFloat(data.total_deposits).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        <p><strong>Total Withdrawals:</strong> $${parseFloat(data.total_withdrawals).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        <p><strong>Total Transfers:</strong> $${parseFloat(data.total_transfers).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        <p><strong>Total Transactions Count:</strong> ${data.total_transactions}</p>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 1rem;">Loan Status Metrics</h3>
        <p><strong>Pending Loans:</strong> ${data.pending_loans}</p>
        <p><strong>Approved Loans:</strong> ${data.approved_loans}</p>
        <p><strong>Rejected Loans:</strong> ${data.rejected_loans}</p>
        <p><strong>Closed Loans:</strong> ${data.closed_loans}</p>
        <div style="margin-top: 1rem;">
          <a href="loans.html" class="btn btn-primary">Manage Loans</a>
        </div>
      </div>
    </div>
  `;
}

// Open Profile Modal for Customer
async function openProfileModal() {
  let profileData = {};
  const res = await fetchWithAuth('/customers/profile/');
  let isNew = true;

  if (res && res.ok) {
    profileData = await res.json();
    isNew = false;
  }

  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">${isNew ? 'Create Customer Profile' : 'Update Customer Profile'}</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>

    <div id="profile-alert" class="alert"></div>

    <form id="profile-form">
      <div class="form-group">
        <label class="form-label">Phone Number</label>
        <input type="text" id="prof-phone" class="form-control" value="${profileData.phone || ''}" required placeholder="+1234567890">
      </div>
      <div class="form-group">
        <label class="form-label">Address</label>
        <textarea id="prof-address" class="form-control" rows="3" required placeholder="123 Main St, City">${profileData.address || ''}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Date of Birth</label>
        <input type="date" id="prof-dob" class="form-control" value="${profileData.date_of_birth || ''}" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">${isNew ? 'Create Profile' : 'Save Changes'}</button>
    </form>
  `;

  modalOverlay.classList.add('active');

  document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const phone = document.getElementById('prof-phone').value;
    const address = document.getElementById('prof-address').value;
    const date_of_birth = document.getElementById('prof-dob').value;

    const method = isNew ? 'POST' : 'PUT';
    const saveRes = await fetchWithAuth('/customers/profile/', {
      method: method,
      body: JSON.stringify({ phone, address, date_of_birth })
    });

    const alertBox = document.getElementById('profile-alert');
    if (saveRes && (saveRes.status === 200 || saveRes.status === 201)) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Profile saved successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        window.location.reload();
      }, 1000);
    } else {
      const err = await saveRes.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

function closeModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  modalOverlay.classList.remove('active');
}
