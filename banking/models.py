import random
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
