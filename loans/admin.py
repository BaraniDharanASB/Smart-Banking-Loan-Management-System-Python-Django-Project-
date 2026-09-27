from django.contrib import admin
from .models import Loan, LoanRepayment

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'customer', 'loan_type', 'amount', 'interest_rate', 'tenure_months', 'status', 'application_date')
    list_filter = ('loan_type', 'status', 'application_date')
    search_fields = ('loan_id', 'customer__user__username', 'customer__user__email')

@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ('repayment_id', 'loan', 'installment_number', 'due_date', 'amount', 'paid_amount', 'status', 'paid_date')
    list_filter = ('status', 'due_date')
    search_fields = ('repayment_id', 'loan__loan_id', 'loan__customer__user__username')
