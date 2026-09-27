from django.contrib import admin
from .models import BankAccount

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'customer', 'account_type', 'balance', 'status', 'created_at')
    list_filter = ('account_type', 'status', 'created_at')
    search_fields = ('account_number', 'customer__user__username', 'customer__user__email')
