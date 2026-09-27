from rest_framework import serializers
from .models import BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    customer_id = serializers.ReadOnlyField(source='customer.id')
    customer_username = serializers.ReadOnlyField(source='customer.user.username')

    class Meta:
        model = BankAccount
        fields = [
            'id',
            'account_number',
            'customer_id',
            'customer_username',
            'account_type',
            'balance',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'account_number', 'customer_id', 'customer_username', 'balance', 'status', 'created_at', 'updated_at']
