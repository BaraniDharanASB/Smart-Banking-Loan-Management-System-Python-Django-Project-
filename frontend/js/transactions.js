// Smart Banking & Loan Management System - Transactions JS

let allTransactions = [];

document.addEventListener('DOMContentLoaded', async () => {
  const profile = await loadUserProfile();
  if (!profile) return;

  renderNavbar();
  await loadTransactions();
});

async function loadTransactions() {
  const container = document.getElementById('transactions-container');
  if (!container) return;

  const response = await fetchWithAuth('/banking/transactions/');
  if (!response || !response.ok) return;

  allTransactions = await response.json();
  renderTransactionTable(allTransactions);
}

function renderTransactionTable(transactions) {
  const container = document.getElementById('transactions-container');

  let html = `
    <div class="page-header">
      <h1 class="page-title">Transaction History</h1>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <label class="form-label" style="margin: 0;">Filter Type:</label>
        <select id="txn-filter" class="form-control" style="width: 150px;" onchange="filterTransactions()">
          <option value="ALL">All Types</option>
          <option value="DEPOSIT">Deposit</option>
          <option value="WITHDRAWAL">Withdrawal</option>
          <option value="TRANSFER">Transfer</option>
        </select>
      </div>
    </div>
  `;

  if (transactions.length === 0) {
    html += `
      <div class="card" style="text-align: center; padding: 3rem;">
        <h3 style="margin-bottom: 0.5rem;">No Transactions Found</h3>
        <p style="color: var(--text-muted);">No transaction records match your criteria.</p>
      </div>
    `;
  } else {
    html += `
      <div class="card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Type</th>
                <th>Source Acc</th>
                <th>Destination Acc</th>
                <th>Amount ($)</th>
                <th>Status</th>
                <th>Reference No</th>
                <th>Date & Time</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${transactions.map(t => `
                <tr>
                  <td><code>${t.transaction_id}</code></td>
                  <td><strong>${t.transaction_type}</strong></td>
                  <td>${t.source_account_number || '-'}</td>
                  <td>${t.destination_account_number || '-'}</td>
                  <td style="font-weight: 700;">$${parseFloat(t.amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
                  <td><small style="color: var(--text-muted);">${t.reference_number}</small></td>
                  <td>${new Date(t.transaction_date).toLocaleString()}</td>
                  <td>${t.description || '-'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function filterTransactions() {
  const filterVal = document.getElementById('txn-filter').value;
  if (filterVal === 'ALL') {
    renderTransactionTable(allTransactions);
  } else {
    const filtered = allTransactions.filter(t => t.transaction_type === filterVal);
    renderTransactionTable(filtered);
    document.getElementById('txn-filter').value = filterVal;
  }
}
