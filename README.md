# Smart Banking & Loan Management System

A full-stack web application designed for core banking operations, account management, atomic financial transactions, loan processing, EMI calculations, repayment management, and role-based dashboard analytics.

---

## 🌟 Features

- **User Authentication & Role Management**:
  - Custom `User` model with roles: `CUSTOMER`, `EMPLOYEE`, `ADMIN`.
  - JWT Authentication using Simple JWT (`/api/auth/token/`, `/api/auth/token/refresh/`).
  - Customer registration (`/api/auth/register/`) automatically assigning `CUSTOMER` role.
  - Protected profile management (`/api/auth/profile/`).

- **Customer Profile & Bank Account Management**:
  - One-to-One linked `Customer` profile (`phone`, `address`, `date_of_birth`).
  - Account opening (`SAVINGS` / `CURRENT`) with auto-generated 12-digit account numbers.
  - Strict isolation ensuring customers access only their own accounts.

- **Deposits, Withdrawals & Atomic Fund Transfers**:
  - Instant cash deposits and withdrawals.
  - Inter-account fund transfers wrapped inside `django.db.transaction.atomic` blocks to guarantee consistency.
  - Non-negative balance enforcement and active account status validation.
  - Full transaction history tracking with unique `transaction_id` and `reference_number`.

- **Loan Processing & Approval Workflow**:
  - Loan application (`PERSONAL`, `EDUCATION`, `HOME`, `VEHICLE`).
  - Automated `PENDING` initial status.
  - Role-based approval and rejection workflows (accessible only to `EMPLOYEE` and `ADMIN` roles).
  - Rejection reason tracking.

- **EMI Calculation & Repayment Schedule**:
  - Exact monthly EMI calculation using standard financial compound interest math (`Decimal` precision).
  - Support for 0% zero-interest EMI calculation (`EMI = Principal / Tenure`).
  - Automatic creation of monthly `LoanRepayment` installment schedules upon loan approval.
  - Repayment payment processing with duplicate payment protection.
  - Automatic loan status update to `CLOSED` upon completing all installment payments.

- **Dashboard & System Analytics**:
  - **Customer Dashboard**: Total active balance, savings vs. current balance, recent 5 transactions, loan summaries, and outstanding loan total.
  - **Employee Dashboard**: System-wide customer counts, active bank accounts, total transaction counts, loan status breakdown, and total loan portfolio amount.
  - **Admin Dashboard**: Comprehensive system statistics, employee count, blocked account tracking, and breakdown of total deposits, withdrawals, and transfers.

- **Responsive Vanilla Frontend**:
  - Built strictly with HTML5, CSS3, and Vanilla JavaScript (ES6 `fetch`).
  - Dynamic navbar, card grids, modal forms, status badges, alert banners, and interactive tables.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 5.2
- **REST Framework**: Django REST Framework (DRF), Simple JWT (`djangorestframework-simplejwt`)
- **CORS Support**: `django-cors-headers`
- **Database**: MySQL 8.0+ (`mysqlclient`)
- **Environment Management**: `python-dotenv`
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (No external frameworks)
- **Version Control**: Git

---

## 📁 Project Structure

```
Smart Banking & Loan Management System/
│
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
├── .gitignore                 # Excluded files list
├── manage.py                 # Django management script
├── requirements.txt          # Dependencies list
├── README.md                 # Project documentation
│
├── smart_banking/            # Django Core Project Settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                 # User Auth & Custom User Model App
│   ├── models.py             # Custom User (AbstractUser) & Role choices
│   ├── serializers.py        # Registration & Profile serializers
│   ├── views.py              # Register & Profile views
│   └── urls.py               # Auth URL routes
│
├── customers/                # Customer Profile App
│   ├── models.py             # Customer profile model
│   ├── serializers.py        # Customer profile serializer
│   ├── views.py              # Profile views (GET, POST, PUT)
│   └── urls.py
│
├── banking/                  # Bank Account & Transaction App
│   ├── models.py             # BankAccount & Transaction models
│   ├── serializers.py        # Account & Transaction serializers
│   ├── views.py              # Deposit, Withdraw, Transfer & Transactions views
│   └── urls.py
│
├── loans/                    # Loan, EMI & Repayment App
│   ├── models.py             # Loan & LoanRepayment models
│   ├── services.py           # EMI math & schedule generator
│   ├── serializers.py        # Loan & Repayment serializers
│   ├── views.py              # Loan application, approve, reject, EMI, pay views
│   └── urls.py
│
├── dashboard/                # Dashboard & Reporting App
│   ├── views.py              # Customer, Employee & Admin dashboard metrics
│   └── urls.py
│
└── frontend/                 # Responsive Vanilla JS Frontend
    ├── index.html            # Landing Page
    ├── login.html            # Login Page
    ├── register.html         # Customer Registration Page
    ├── dashboard.html        # Role-based Dashboard
    ├── accounts.html         # Bank Accounts Management
    ├── transactions.html     # Transaction History
    ├── loans.html            # Loans & Repayments Management
    ├── css/
    │   └── style.css         # Professional Banking Styling
    └── js/
        ├── auth.js           # Token & Auth Helpers
        ├── dashboard.js      # Dashboard & Profile Handler
        ├── accounts.js       # Accounts, Deposit, Withdraw, Transfer Handler
        ├── transactions.js   # Transactions Table & Filters
        └── loans.js          # Loans, EMI, Repayments, Approvals Handler
```

---

## 🔑 Environment Variables (`.env`)

Create a `.env` file in the project root based on `.env.example`:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True

DB_NAME=smart_banking_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

ALLOWED_HOSTS=127.0.0.1,localhost,testserver
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000
```

---

## 🛢️ MySQL Database Setup

1. Log in to your MySQL server terminal/client:
   ```sql
   CREATE DATABASE smart_banking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

---

## ⚙️ Backend Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd "Smart Banking & Loan Management System"
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # On Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations & system check**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py check
   ```

5. **Start the Django backend server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

---

## 🌐 Frontend Setup & How to Run

1. Open a web browser or use Live Server extension / Python HTTP server to serve the `frontend/` directory.
2. Example using Python's built-in HTTP server:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
3. Navigate to `http://127.0.0.1:5500` or `http://localhost:5500` in your web browser.

---

## 📡 API Overview & Endpoints

| Module | Method | Endpoint | Description | Access |
|---|---|---|---|---|
| **Auth** | `POST` | `/api/auth/register/` | Register new customer | Public |
| **Auth** | `POST` | `/api/auth/token/` | Obtain JWT tokens | Public |
| **Auth** | `POST` | `/api/auth/token/refresh/` | Refresh JWT access token | Public |
| **Auth** | `GET` | `/api/auth/profile/` | Get user profile | Authenticated |
| **Customer** | `POST/GET/PUT` | `/api/customers/profile/` | Create, view, update customer profile | Customer |
| **Banking** | `POST/GET` | `/api/banking/accounts/` | Open or list bank accounts | Authenticated |
| **Banking** | `GET` | `/api/banking/accounts/<id>/` | View account details | Owner / Staff |
| **Banking** | `POST` | `/api/banking/deposit/` | Deposit cash into account | Owner / Staff |
| **Banking** | `POST` | `/api/banking/withdraw/` | Withdraw cash from account | Owner / Staff |
| **Banking** | `POST` | `/api/banking/transfer/` | Atomically transfer funds | Owner / Staff |
| **Banking** | `GET` | `/api/banking/transactions/` | View transaction history | Authenticated |
| **Loans** | `POST/GET` | `/api/loans/` | Apply for loan or list loans | Authenticated |
| **Loans** | `GET` | `/api/loans/<id>/` | View loan detail | Owner / Staff |
| **Loans** | `POST` | `/api/loans/<id>/approve/` | Approve pending loan application | Employee / Admin |
| **Loans** | `POST` | `/api/loans/<id>/reject/` | Reject pending loan application | Employee / Admin |
| **Loans** | `GET` | `/api/loans/<id>/emi/` | View EMI calculation details | Owner / Staff |
| **Loans** | `GET` | `/api/loans/<id>/repayments/` | View repayment schedule | Owner / Staff |
| **Loans** | `POST` | `/api/loans/<id>/repayments/<rid>/pay/` | Pay loan repayment installment | Owner / Staff |
| **Dashboard** | `GET` | `/api/dashboard/customer/` | Customer analytics & 5 recent txns | Customer |
| **Dashboard** | `GET` | `/api/dashboard/employee/` | Employee system statistics | Employee / Admin |
| **Dashboard** | `GET` | `/api/dashboard/admin/` | Admin system & financial totals | Admin |

---

## 👥 User Roles & Permissions

- **CUSTOMER**: Can create profile, open accounts, make deposits/withdrawals/transfers, apply for loans, calculate EMI, pay repayments, and view customer dashboard.
- **EMPLOYEE**: Can view all accounts, transactions, and loans, approve or reject pending loans, and view the Employee Dashboard.
- **ADMIN**: Has complete system-wide management privileges including view of all financial totals, employee counts, blocked accounts, and Admin Dashboard.

---

## 🧪 Testing Instructions

1. **Verify Database & System Check**:
   ```bash
   python manage.py check
   python manage.py migrate
   ```

2. **Complete End-to-End Workflow Test**:
   - Register a customer (`/register.html`).
   - Log in (`/login.html`) and obtain JWT tokens.
   - Complete customer profile (`/dashboard.html`).
   - Open a Savings account (`/accounts.html`).
   - Deposit $5,000 into the account.
   - Withdraw $1,000 from the account.
   - Open a second Current account and transfer $1,500.
   - Inspect transaction history (`/transactions.html`).
   - Apply for a Personal Loan (`/loans.html`).
   - Log in as Employee and approve the loan (`/loans.html`).
   - Log back in as Customer, view EMI schedule and pay installments.
   - Observe automatic loan status transition to `CLOSED` upon completing all repayments.
   - Inspect Customer, Employee, and Admin Dashboards (`/dashboard.html`).
