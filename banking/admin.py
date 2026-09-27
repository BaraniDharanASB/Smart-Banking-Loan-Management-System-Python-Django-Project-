from django.contrib import admin
from .models import BankAccount, Transaction

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'customer', 'account_type', 'balance', 'status', 'created_at')
    list_filter = ('account_type', 'status', 'created_at')
    search_fields = ('account_number', 'customer__user__username', 'customer__user__email')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'source_account', 'destination_account', 'amount', 'status', 'transaction_date')
    list_filter = ('transaction_type', 'status', 'transaction_date')
    search_fields = ('transaction_id', 'reference_number', 'source_account__account_number', 'destination_account__account_number')
