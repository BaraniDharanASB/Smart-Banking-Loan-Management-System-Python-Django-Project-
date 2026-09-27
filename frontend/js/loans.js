// Smart Banking & Loan Management System - Loans JS

let allLoans = [];

document.addEventListener('DOMContentLoaded', async () => {
  const profile = await loadUserProfile();
  if (!profile) return;

  renderNavbar();
  await loadLoans();
});

async function loadLoans() {
  const container = document.getElementById('loans-container');
  if (!container) return;

  const response = await fetchWithAuth('/loans/');
  if (!response || !response.ok) return;

  allLoans = await response.json();
  const profile = getUserProfile();

  let html = `
    <div class="page-header">
      <h1 class="page-title">Loan Management</h1>
      ${profile.role === 'CUSTOMER' ? '<button onclick="openApplyLoanModal()" class="btn btn-primary">+ Apply for Loan</button>' : ''}
    </div>
  `;

  if (allLoans.length === 0) {
    html += `
      <div class="card" style="text-align: center; padding: 3rem;">
        <h3 style="margin-bottom: 0.5rem;">No Loan Applications Found</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">There are no loan applications recorded in the system.</p>
        ${profile.role === 'CUSTOMER' ? '<button onclick="openApplyLoanModal()" class="btn btn-primary">Apply Now</button>' : ''}
      </div>
    `;
  } else {
    html += `
      <div class="card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Loan ID</th>
                <th>Applicant</th>
                <th>Type</th>
                <th>Amount ($)</th>
                <th>Rate (%)</th>
                <th>Tenure</th>
                <th>Status</th>
                <th>Applied Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${allLoans.map(loan => `
                <tr>
                  <td><code>${loan.loan_id}</code></td>
                  <td><strong>${loan.customer_username || 'Self'}</strong></td>
                  <td>${loan.loan_type}</td>
                  <td style="font-weight: 700;">$${parseFloat(loan.amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td>${loan.interest_rate}%</td>
                  <td>${loan.tenure_months} mos</td>
                  <td><span class="badge badge-${loan.status.toLowerCase()}">${loan.status}</span></td>
                  <td>${new Date(loan.application_date).toLocaleDateString()}</td>
                  <td>
                    <div style="display: flex; gap: 0.35rem; flex-wrap: wrap;">
                      ${(loan.status === 'APPROVED' || loan.status === 'CLOSED') ? `
                        <button onclick="viewEMIModal(${loan.id})" class="btn btn-sm btn-secondary">EMI</button>
                        <button onclick="viewRepaymentsModal(${loan.id})" class="btn btn-sm btn-primary">Schedule</button>
                      ` : ''}

                      ${(profile.role === 'EMPLOYEE' || profile.role === 'ADMIN') && loan.status === 'PENDING' ? `
                        <button onclick="approveLoan(${loan.id})" class="btn btn-sm btn-success">Approve</button>
                        <button onclick="openRejectLoanModal(${loan.id})" class="btn btn-sm btn-danger">Reject</button>
                      ` : ''}

                      ${loan.status === 'REJECTED' ? `<span style="font-size: 0.8rem; color: var(--danger-color);" title="${loan.rejection_reason}">Reason: ${loan.rejection_reason}</span>` : ''}
                    </div>
                  </td>
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

// Open Apply for Loan Modal
function openApplyLoanModal() {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Apply for a Loan</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="loan-alert" class="alert"></div>
    <form id="apply-loan-form">
      <div class="form-group">
        <label class="form-label">Loan Type</label>
        <select id="loan-type" class="form-control" required>
          <option value="PERSONAL">Personal Loan</option>
          <option value="EDUCATION">Education Loan</option>
          <option value="HOME">Home Loan</option>
          <option value="VEHICLE">Vehicle Loan</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Loan Amount ($)</label>
        <input type="number" step="0.01" min="0.01" id="loan-amount" class="form-control" required placeholder="100000.00">
      </div>
      <div class="form-group">
        <label class="form-label">Annual Interest Rate (%)</label>
        <input type="number" step="0.01" min="0.00" id="loan-rate" class="form-control" required placeholder="10.5">
      </div>
      <div class="form-group">
        <label class="form-label">Tenure (Months)</label>
        <input type="number" min="1" id="loan-tenure" class="form-control" required placeholder="24">
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Submit Loan Application</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('apply-loan-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const loan_type = document.getElementById('loan-type').value;
    const amount = document.getElementById('loan-amount').value;
    const interest_rate = document.getElementById('loan-rate').value;
    const tenure_months = document.getElementById('loan-tenure').value;

    const res = await fetchWithAuth('/loans/', {
      method: 'POST',
      body: JSON.stringify({ loan_type, amount, interest_rate, tenure_months })
    });

    const alertBox = document.getElementById('loan-alert');
    if (res && res.status === 201) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Loan application submitted successfully!';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadLoans();
      }, 1000);
    } else {
      const err = await res.json();
      alertBox.className = 'alert alert-danger';
      alertBox.textContent = JSON.stringify(err);
      alertBox.style.display = 'block';
    }
  });
}

// View EMI Calculation Modal
async function viewEMIModal(loanId) {
  const res = await fetchWithAuth(`/loans/${loanId}/emi/`);
  if (!res || !res.ok) return;

  const emi = await res.json();

  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">EMI Calculation Details</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="card" style="box-shadow: none; border: 1px solid var(--border-color);">
      <p style="margin-bottom: 0.5rem;"><strong>Loan ID:</strong> <code>${emi.loan_id}</code></p>
      <p style="margin-bottom: 0.5rem;"><strong>Principal Amount:</strong> $${parseFloat(emi.principal).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
      <p style="margin-bottom: 0.5rem;"><strong>Annual Interest Rate:</strong> ${emi.interest_rate}%</p>
      <p style="margin-bottom: 0.5rem;"><strong>Tenure:</strong> ${emi.tenure_months} Months</p>
      <hr style="margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);" />
      <div style="font-size: 1.1rem; color: var(--accent-color); margin-bottom: 0.5rem;">
        <strong>Monthly EMI:</strong> $${parseFloat(emi.monthly_emi).toLocaleString(undefined, {minimumFractionDigits: 2})}
      </div>
      <p style="margin-bottom: 0.25rem;"><strong>Total Interest Payable:</strong> $${parseFloat(emi.total_interest).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
      <p><strong>Total Repayment Amount:</strong> $${parseFloat(emi.total_payment).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
    </div>
  `;
  modalOverlay.classList.add('active');
}

// View Repayment Schedule Modal
async function viewRepaymentsModal(loanId) {
  const res = await fetchWithAuth(`/loans/${loanId}/repayments/`);
  if (!res || !res.ok) return;

  const repayments = await res.json();
  const profile = getUserProfile();

  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Repayment Schedule</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="pay-alert" class="alert"></div>
    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
      <table class="data-table">
        <thead>
          <tr>
            <th>Inst #</th>
            <th>Due Date</th>
            <th>Amount ($)</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${repayments.map(r => `
            <tr>
              <td>#${r.installment_number}</td>
              <td>${r.due_date}</td>
              <td style="font-weight: 700;">$${parseFloat(r.amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
              <td><span class="badge badge-${r.status.toLowerCase()}">${r.status}</span></td>
              <td>
                ${r.status === 'PENDING' ? `
                  <button onclick="payInstallment(${loanId}, ${r.id})" class="btn btn-sm btn-success">Pay Now</button>
                ` : `<span style="font-size: 0.8rem; color: var(--success-color);">Paid on ${new Date(r.paid_date).toLocaleDateString()}</span>`}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
  modalOverlay.classList.add('active');
}

// Pay Installment
async function payInstallment(loanId, repaymentId) {
  const alertBox = document.getElementById('pay-alert');
  const res = await fetchWithAuth(`/loans/${loanId}/repayments/${repaymentId}/pay/`, {
    method: 'POST'
  });

  if (res && res.status === 200) {
    const data = await res.json();
    alertBox.className = 'alert alert-success';
    alertBox.textContent = `Installment paid! Loan Status: ${data.loan_status}`;
    alertBox.style.display = 'block';
    setTimeout(() => {
      viewRepaymentsModal(loanId);
      loadLoans();
    }, 1000);
  } else {
    const err = await res.json();
    alertBox.className = 'alert alert-danger';
    alertBox.textContent = JSON.stringify(err);
    alertBox.style.display = 'block';
  }
}

// Approve Loan (Employee/Admin)
async function approveLoan(loanId) {
  if (!confirm('Are you sure you want to approve this loan application?')) return;

  const res = await fetchWithAuth(`/loans/${loanId}/approve/`, { method: 'POST' });
  if (res && res.status === 200) {
    alert('Loan approved successfully!');
    loadLoans();
  } else {
    const err = await res.json();
    alert(JSON.stringify(err));
  }
}

// Open Reject Loan Modal (Employee/Admin)
function openRejectLoanModal(loanId) {
  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  modalContent.innerHTML = `
    <div class="modal-header">
      <h2 class="modal-title">Reject Loan Application</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div id="rej-alert" class="alert"></div>
    <form id="reject-loan-form">
      <div class="form-group">
        <label class="form-label">Rejection Reason</label>
        <textarea id="rej-reason" class="form-control" rows="3" required placeholder="State reason for rejection..."></textarea>
      </div>
      <button type="submit" class="btn btn-danger" style="width: 100%;">Confirm Rejection</button>
    </form>
  `;
  modalOverlay.classList.add('active');

  document.getElementById('reject-loan-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const rejection_reason = document.getElementById('rej-reason').value;

    const res = await fetchWithAuth(`/loans/${loanId}/reject/`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason })
    });

    const alertBox = document.getElementById('rej-alert');
    if (res && res.status === 200) {
      alertBox.className = 'alert alert-success';
      alertBox.textContent = 'Loan application rejected.';
      alertBox.style.display = 'block';
      setTimeout(() => {
        closeModal();
        loadLoans();
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
