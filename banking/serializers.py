from decimal import Decimal
from rest_framework import serializers
from .models import BankAccount, Transaction

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


class DepositSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'), required=True)
    description = serializers.CharField(required=False, allow_blank=True, default="Cash deposit")


class WithdrawSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'), required=True)
    description = serializers.CharField(required=False, allow_blank=True, default="Cash withdrawal")


class TransferSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField(required=True)
    destination_account_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'), required=True)
    description = serializers.CharField(required=False, allow_blank=True, default="Fund transfer")

    def validate(self, data):
        if data['source_account_id'] == data['destination_account_id']:
            raise serializers.ValidationError("Transfers to the same account are not allowed.")
        return data


class TransactionSerializer(serializers.ModelSerializer):
    source_account_number = serializers.ReadOnlyField(source='source_account.account_number')
    destination_account_number = serializers.ReadOnlyField(source='destination_account.account_number')

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'transaction_type',
            'source_account',
            'source_account_number',
            'destination_account',
            'destination_account_number',
            'amount',
            'status',
            'reference_number',
            'transaction_date',
            'description'
        ]
