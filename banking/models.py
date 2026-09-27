import random
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from customers.models import Customer

class BankAccount(models.Model):
    class AccountType(models.TextChoices):
        SAVINGS = 'SAVINGS', 'Savings'
        CURRENT = 'CURRENT', 'Current'

    class AccountStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        BLOCKED = 'BLOCKED', 'Blocked'
        CLOSED = 'CLOSED', 'Closed'

    account_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='accounts'
    )
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.SAVINGS
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_unique_account_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_account_number(cls):
        while True:
            number = f"10{random.randint(1000000000, 9999999999)}"
            if not cls.objects.filter(account_number=number).exists():
                return number

    def __str__(self):
        return f"Account {self.account_number} ({self.account_type}) - Balance: {self.balance}"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Deposit'
        WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
        TRANSFER = 'TRANSFER', 'Transfer'

    class TransactionStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    source_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transactions'
    )
    destination_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transactions'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.SUCCESS
    )
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_unique_transaction_id()
        if not self.reference_number:
            self.reference_number = self.generate_unique_reference_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_transaction_id(cls):
        while True:
            tid = f"TXN{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(transaction_id=tid).exists():
                return tid

    @classmethod
    def generate_unique_reference_number(cls):
        while True:
            ref = f"REF{random.randint(100000000000, 999999999999)}"
            if not cls.objects.filter(reference_number=ref).exists():
                return ref

    def __str__(self):
        return f"{self.transaction_type} {self.transaction_id} - {self.amount} ({self.status})"
