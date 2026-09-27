from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'customer', 'loan_type', 'amount', 'interest_rate', 'tenure_months', 'status', 'application_date')
    list_filter = ('loan_type', 'status', 'application_date')
    search_fields = ('loan_id', 'customer__user__username', 'customer__user__email')
