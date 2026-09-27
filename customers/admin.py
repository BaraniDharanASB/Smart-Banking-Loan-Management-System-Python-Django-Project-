from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
