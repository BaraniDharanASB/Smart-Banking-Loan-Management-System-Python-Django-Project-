from decimal import Decimal
from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from customers.models import Customer
from banking.models import BankAccount, Transaction
from banking.serializers import TransactionSerializer
from loans.models import Loan, LoanRepayment

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_dashboard(request):
    """
    GET: Retrieve dashboard metrics for the authenticated customer.
    """
    user = request.user
    try:
        customer = user.customer_profile
    except Customer.DoesNotExist:
        return Response(
            {'detail': 'Customer profile not found. Please create a customer profile first.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    accounts = BankAccount.objects.filter(customer=customer)
    total_bank_accounts = accounts.count()

    active_accounts = accounts.filter(status=BankAccount.AccountStatus.ACTIVE)
    total_balance = active_accounts.aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')

    savings_balance = active_accounts.filter(
        account_type=BankAccount.AccountType.SAVINGS
    ).aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')

    current_balance = active_accounts.filter(
        account_type=BankAccount.AccountType.CURRENT
    ).aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')

    transactions_qs = Transaction.objects.filter(
        Q(source_account__customer=customer) | Q(destination_account__customer=customer)
    ).distinct().order_by('-transaction_date')

    total_transactions = transactions_qs.count()
    recent_transactions = TransactionSerializer(transactions_qs[:5], many=True).data

    loans = Loan.objects.filter(customer=customer)
    total_loans = loans.count()
    pending_loans = loans.filter(status=Loan.LoanStatus.PENDING).count()
    approved_loans = loans.filter(status=Loan.LoanStatus.APPROVED).count()
    rejected_loans = loans.filter(status=Loan.LoanStatus.REJECTED).count()
    closed_loans = loans.filter(status=Loan.LoanStatus.CLOSED).count()

    outstanding = LoanRepayment.objects.filter(
        loan__customer=customer,
        loan__status=Loan.LoanStatus.APPROVED,
        status=LoanRepayment.RepaymentStatus.PENDING
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    customer_name = user.get_full_name() or user.username

    return Response({
        'customer_name': customer_name,
        'total_bank_accounts': total_bank_accounts,
        'total_balance': str(total_balance),
        'savings_account_balance': str(savings_balance),
        'current_account_balance': str(current_balance),
        'total_transactions': total_transactions,
        'recent_transactions': recent_transactions,
        'total_loans': total_loans,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'closed_loans': closed_loans,
        'total_outstanding_loan_amount': str(outstanding)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_dashboard(request):
    """
    GET: Retrieve system-wide metrics for EMPLOYEE and ADMIN roles.
    """
    user = request.user
    if user.role not in [User.Role.EMPLOYEE, User.Role.ADMIN] and not user.is_staff:
        return Response(
            {'detail': 'You do not have permission to access the employee dashboard.'},
            status=status.HTTP_403_FORBIDDEN
        )

    total_customers = Customer.objects.count()
    total_bank_accounts = BankAccount.objects.count()
    total_active_accounts = BankAccount.objects.filter(status=BankAccount.AccountStatus.ACTIVE).count()
    total_transactions = Transaction.objects.count()

    total_loans = Loan.objects.count()
    pending_loans = Loan.objects.filter(status=Loan.LoanStatus.PENDING).count()
    approved_loans = Loan.objects.filter(status=Loan.LoanStatus.APPROVED).count()
    rejected_loans = Loan.objects.filter(status=Loan.LoanStatus.REJECTED).count()
    closed_loans = Loan.objects.filter(status=Loan.LoanStatus.CLOSED).count()

    total_loan_amount = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    return Response({
        'total_customers': total_customers,
        'total_bank_accounts': total_bank_accounts,
        'total_active_accounts': total_active_accounts,
        'total_transactions': total_transactions,
        'total_loans': total_loans,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'closed_loans': closed_loans,
        'total_loan_amount': str(total_loan_amount)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """
    GET: Retrieve system-wide metrics and financial totals for ADMIN role only.
    """
    user = request.user
    if user.role != User.Role.ADMIN and not user.is_superuser:
        return Response(
            {'detail': 'You do not have permission to access the admin dashboard.'},
            status=status.HTTP_403_FORBIDDEN
        )

    total_employees = User.objects.filter(role=User.Role.EMPLOYEE).count()
    total_customers = Customer.objects.count()
    total_bank_accounts = BankAccount.objects.count()
    total_active_accounts = BankAccount.objects.filter(status=BankAccount.AccountStatus.ACTIVE).count()
    total_blocked_accounts = BankAccount.objects.filter(status=BankAccount.AccountStatus.BLOCKED).count()
    total_transactions = Transaction.objects.count()

    total_deposits = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.DEPOSIT,
        status=Transaction.TransactionStatus.SUCCESS
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    total_withdrawals = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.WITHDRAWAL,
        status=Transaction.TransactionStatus.SUCCESS
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    total_transfers = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.TRANSFER,
        status=Transaction.TransactionStatus.SUCCESS
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    total_loans = Loan.objects.count()
    pending_loans = Loan.objects.filter(status=Loan.LoanStatus.PENDING).count()
    approved_loans = Loan.objects.filter(status=Loan.LoanStatus.APPROVED).count()
    rejected_loans = Loan.objects.filter(status=Loan.LoanStatus.REJECTED).count()
    closed_loans = Loan.objects.filter(status=Loan.LoanStatus.CLOSED).count()

    total_loan_amount = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    return Response({
        'total_employees': total_employees,
        'total_customers': total_customers,
        'total_bank_accounts': total_bank_accounts,
        'total_active_accounts': total_active_accounts,
        'total_blocked_accounts': total_blocked_accounts,
        'total_transactions': total_transactions,
        'total_deposits': str(total_deposits),
        'total_withdrawals': str(total_withdrawals),
        'total_transfers': str(total_transfers),
        'total_loans': total_loans,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'closed_loans': closed_loans,
        'total_loan_amount': str(total_loan_amount)
    }, status=status.HTTP_200_OK)
