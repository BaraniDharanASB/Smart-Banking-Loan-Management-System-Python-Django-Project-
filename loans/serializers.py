from decimal import Decimal
from rest_framework import serializers
from .models import Loan

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'interest_rate', 'tenure_months']
        extra_kwargs = {
            'amount': {'min_value': Decimal('0.01'), 'required': True},
            'interest_rate': {'min_value': Decimal('0.00'), 'required': True},
            'tenure_months': {'min_value': 1, 'required': True},
            'loan_type': {'required': True},
        }


class LoanRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=True, allow_blank=False)


class LoanDetailSerializer(serializers.ModelSerializer):
    customer_id = serializers.ReadOnlyField(source='customer.id')
    customer_username = serializers.ReadOnlyField(source='customer.user.username')

    class Meta:
        model = Loan
        fields = [
            'id',
            'loan_id',
            'customer_id',
            'customer_username',
            'loan_type',
            'amount',
            'interest_rate',
            'tenure_months',
            'status',
            'application_date',
            'approved_date',
            'rejection_reason',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
