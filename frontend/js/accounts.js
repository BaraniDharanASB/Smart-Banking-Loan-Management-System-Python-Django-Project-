// Smart Banking & Loan Management System - Accounts JS

let userAccounts = [];

document.addEventListener('DOMContentLoaded', async () => {
  const profile = await loadUserProfile();
  if (!profile) return;

  renderNavbar();
  await loadAccounts();
});

async function loadAccounts() {
  const container = document.getElementById('accounts-container');
  if (!container) return;

  const response = await fetchWithAuth('/banking/accounts/');
  if (!response || !response.ok) return;

  userAccounts = await response.json();
  const profile = getUserProfile();

  let html = `
    <div class="page-header">
      <h1 class="page-title">Bank Accounts</h1>
      <div style="display: flex; gap: 0.5rem;">
        ${profile.role === 'CUSTOMER' ? `
          <button onclick="openCreateAccountModal()" class="btn btn-primary">+ Open Account</button>
          <button onclick="openDepositModal()" class="btn btn-success">Deposit</button>
          <button onclick="openWithdrawModal()" class="btn btn-secondary">Withdraw</button>
          <button onclick="openTransferModal()" class="btn btn-secondary">Transfer</button>
        ` : ''}
      </div>
    </div>
  `;

  if (userAccounts.length === 0) {
    html += `
      <div class="card" style="text-align: center; padding: 3rem;">
        <h3 style="margin-bottom: 0.5rem;">No Bank Accounts Found</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">You do not have any active bank accounts registered.</p>
        ${profile.role === 'CUSTOMER' ? '<button onclick="openCreateAccountModal()" class="btn btn-primary">Open Savings or Current Account</button>' : ''}
      </div>
    `;
  } else {
    html += `
      <div class="grid grid-cols-3" style="margin-bottom: 2rem;">
        ${userAccounts.map(acc => `
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
              <div>
                <span class="badge badge-secondary">${acc.account_type}</span>
                <span class="badge badge-${acc.status.toLowerCase()}">${acc.status}</span>
              </div>
              <small style="color: var(--text-muted);">ID: #${acc.id}</small>
            </div>
            <div class="card-title">Account Number</div>
            <div style="font-family: monospace; font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; color: var(--primary-color);">
              ${acc.account_number}
            </div>
            <div class="card-title">Balance</div>
            <div class="card-value">$${parseFloat(acc.balance).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
            ${acc.customer_username ? `<p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">Owner: <strong>${acc.customer_username}</strong></p>` : ''}
          </div>
        `).join('')}
      </div>
    `;
  }

  container.innerHTML = html;
}

// Open Create Account Modal
function openCreateAccountModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Open New Bank Account</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="acc-alert" class="alert"></div>
    <form id="create-acc-form">
      <div class="form-group">
        <label class="form-label">Account Type</label>
        <select id="acc-type" class="form-control" required>
          <option value="SAVINGS">Savings Account</option>
          <option value="CURRENT">Current Account</option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Create Account</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('create-acc-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = document.getElementById('acc-type').value;

    const res = await fetchWithAuth('/banking/accounts/', {
      method: 'POST',
      body: JSON.stringify({ account_type: type })
    });

    const alertBox = document.getElementById('acc-alert');
    if (res && res.status === 201) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Bank account created successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadAccounts();
      }, 1000);
    } else {
      const err = await res.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

// Open Deposit Modal
function openDepositModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  const options = userAccounts.map(a => `<option value="${a.id}">${a.account_type} - ${a.account_number} (Bal: $${a.balance})</option>`).join('');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Deposit Funds</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="dep-alert" class="alert"></div>
    <form id="deposit-form">
      <div class="form-group">
        <label class="form-label">Select Account</label>
        <select id="dep-acc-id" class="form-control" required>${options}</select>
      </div>
      <div class="form-group">
        <label class="form-label">Deposit Amount ($)</label>
        <input type="number" step="0.01" min="0.01" id="dep-amount" class="form-control" required placeholder="500.00">
      </div>
      <div class="form-group">
        <label class="form-label">Description</label>
        <input type="text" id="dep-desc" class="form-control" placeholder="Cash Deposit">
      </div>
      <button type="submit" class="btn btn-success" style="width: 100%;">Confirm Deposit</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('deposit-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const account_id = document.getElementById('dep-acc-id').value;
    const amount = document.getElementById('dep-amount').value;
    const description = document.getElementById('dep-desc').value || 'Cash deposit';

    const res = await fetchWithAuth('/banking/deposit/', {
      method: 'POST',
      body: JSON.stringify({ account_id, amount, description })
    });

    const alertBox = document.getElementById('dep-alert');
    if (res && res.status === 200) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Deposit completed successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadAccounts();
      }, 1000);
    } else {
      const err = await res.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

// Open Withdraw Modal
function openWithdrawModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  const options = userAccounts.map(a => `<option value="${a.id}">${a.account_type} - ${a.account_number} (Bal: $${a.balance})</option>`).join('');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Withdraw Funds</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="with-alert" class="alert"></div>
    <form id="withdraw-form">
      <div class="form-group">
        <label class="form-label">Select Account</label>
        <select id="with-acc-id" class="form-control" required>${options}</select>
      </div>
      <div class="form-group">
        <label class="form-label">Withdrawal Amount ($)</label>
        <input type="number" step="0.01" min="0.01" id="with-amount" class="form-control" required placeholder="100.00">
      </div>
      <div class="form-group">
        <label class="form-label">Description</label>
        <input type="text" id="with-desc" class="form-control" placeholder="ATM Withdrawal">
      </div>
      <button type="submit" class="btn btn-secondary" style="width: 100%;">Confirm Withdrawal</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('withdraw-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const account_id = document.getElementById('with-acc-id').value;
    const amount = document.getElementById('with-amount').value;
    const description = document.getElementById('with-desc').value || 'Cash withdrawal';

    const res = await fetchWithAuth('/banking/withdraw/', {
      method: 'POST',
      body: JSON.stringify({ account_id, amount, description })
    });

    const alertBox = document.getElementById('with-alert');
    if (res && res.status === 200) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Withdrawal completed successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadAccounts();
      }, 1000);
    } else {
      const err = await res.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

// Open Transfer Modal
function openTransferModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  const options = userAccounts.map(a => `<option value="${a.id}">${a.account_type} - ${a.account_number} (Bal: $${a.balance})</option>`).join('');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Fund Transfer</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="trans-alert" class="alert"></div>
    <form id="transfer-form">
      <div class="form-group">
        <label class="form-label">Source Account</label>
        <select id="trans-src-id" class="form-control" required>${options}</select>
      </div>
      <div class="form-group">
        <label class="form-label">Destination Account ID (ID number)</label>
        <input type="number" id="trans-dest-id" class="form-control" required placeholder="Enter Destination Account ID">
      </div>
      <div class="form-group">
        <label class="form-label">Transfer Amount ($)</label>
        <input type="number" step="0.01" min="0.01" id="trans-amount" class="form-control" required placeholder="250.00">
      </div>
      <div class="form-group">
        <label class="form-label">Description</label>
        <input type="text" id="trans-desc" class="form-control" placeholder="Fund transfer">
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Execute Transfer</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('transfer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const source_account_id = document.getElementById('trans-src-id').value;
    const destination_account_id = document.getElementById('trans-dest-id').value;
    const amount = document.getElementById('trans-amount').value;
    const description = document.getElementById('trans-desc').value || 'Fund transfer';

    const res = await fetchWithAuth('/banking/transfer/', {
      method: 'POST',
      body: JSON.stringify({ source_account_id, destination_account_id, amount, description })
    });

    const alertBox = document.getElementById('trans-alert');
    if (res && res.status === 200) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Fund transfer completed successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadAccounts();
      }, 1000);
    } else {
      const err = await res.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
}
