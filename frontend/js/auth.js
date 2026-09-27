// Smart Banking & Loan Management System - Auth JS

const API_BASE_URL = 'http://127.0.0.1:8000/api';

function getAccessToken() {
  return localStorage.getItem('access_token');
}

function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

function setTokens(access, refresh) {
  if (access) localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}

function setUserProfile(profile) {
  localStorage.setItem('user_profile', JSON.stringify(profile));
}

function getUserProfile() {
  const profile = localStorage.getItem('user_profile');
  return profile ? JSON.parse(profile) : null;
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_profile');
}

function logout() {
  clearAuth();
  window.location.href = 'login.html';
}

// Wrapper around fetch to automatically attach JWT token and handle token refresh
async function fetchWithAuth(endpoint, options = {}) {
  let token = getAccessToken();
  if (!token) {
    window.location.href = 'login.html';
    return null;
  }

  options.headers = options.headers || {};
  options.headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData) && !options.headers['Content-Type']) {
    options.headers['Content-Type'] = 'application/json';
  }

  let response = await fetch(`${API_BASE_URL}${endpoint}`, options);

  // If 401 Unauthorized, try refreshing token once
  if (response.status === 401) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      const refreshResponse = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json();
        setTokens(refreshData.access, null);
        options.headers['Authorization'] = `Bearer ${refreshData.access}`;
        response = await fetch(`${API_BASE_URL}${endpoint}`, options);
      } else {
        logout();
        return null;
      }
    } else {
      logout();
      return null;
    }
  }

  return response;
}

// Fetch current user profile from backend
async function loadUserProfile() {
  const response = await fetchWithAuth('/auth/profile/');
  if (response && response.ok) {
    const profile = await response.json();
    setUserProfile(profile);
    return profile;
  }
  return null;
}

// Render dynamic navbar based on role
function renderNavbar() {
  const navbarElement = document.getElementById('navbar-container');
  if (!navbarElement) return;

  const profile = getUserProfile();
  const isLoggedIn = !!getAccessToken();

  let navHTML = `
    <header>
      <nav class="navbar">
        <a href="${isLoggedIn ? 'dashboard.html' : 'index.html'}" class="nav-brand">
          🏦 Smart Banking System
        </a>
        <ul class="nav-links">
  `;

  if (isLoggedIn && profile) {
    const role = profile.role;
    navHTML += `
      <li><a href="dashboard.html" id="nav-dashboard">Dashboard</a></li>
      <li><a href="accounts.html" id="nav-accounts">Accounts</a></li>
      <li><a href="transactions.html" id="nav-transactions">Transactions</a></li>
      <li><a href="loans.html" id="nav-loans">Loans</a></li>
      <li>
        <span class="user-badge">${profile.username} (${role})</span>
      </li>
      <li>
        <button onclick="logout()" class="btn-logout">Logout</button>
      </li>
    `;
  } else {
    navHTML += `
      <li><a href="index.html">Home</a></li>
      <li><a href="login.html" class="btn btn-sm btn-primary">Login</a></li>
      <li><a href="register.html" class="btn btn-sm btn-secondary">Register</a></li>
    `;
  }

  navHTML += `
        </ul>
      </nav>
    </header>
  `;

  navbarElement.innerHTML = navHTML;

  // Active page highlight
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  if (currentPage.includes('dashboard')) document.getElementById('nav-dashboard')?.classList.add('active');
  if (currentPage.includes('accounts')) document.getElementById('nav-accounts')?.classList.add('active');
  if (currentPage.includes('transactions')) document.getElementById('nav-transactions')?.classList.add('active');
  if (currentPage.includes('loans')) document.getElementById('nav-loans')?.classList.add('active');
}

// Auto render navbar on page load
document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();
});
