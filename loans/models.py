import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from customers.models import Customer

class Loan(models.Model):
    class LoanType(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal Loan'
        EDUCATION = 'EDUCATION', 'Education Loan'
        HOME = 'HOME', 'Home Loan'
        VEHICLE = 'VEHICLE', 'Vehicle Loan'

    class LoanStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CLOSED = 'CLOSED', 'Closed'

    loan_id = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    loan_type = models.CharField(max_length=20, choices=LoanType.choices)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tenure_months = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    status = models.CharField(
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.PENDING
    )
    application_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = self.generate_unique_loan_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_loan_id(cls):
        while True:
            lid = f"LOAN{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(loan_id=lid).exists():
                return lid

    def __str__(self):
        return f"{self.loan_type} {self.loan_id} - {self.amount} ({self.status})"


class LoanRepayment(models.Model):
    class RepaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    repayment_id = models.CharField(max_length=50, unique=True, editable=False)
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status = models.CharField(
        max_length=20,
        choices=RepaymentStatus.choices,
        default=RepaymentStatus.PENDING
    )
    paid_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('loan', 'installment_number')
        ordering = ['installment_number']

    def save(self, *args, **kwargs):
        if not self.repayment_id:
            self.repayment_id = self.generate_unique_repayment_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_repayment_id(cls):
        while True:
            rid = f"PAY{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(repayment_id=rid).exists():
                return rid

    def __str__(self):
        return f"Repayment #{self.installment_number} for Loan {self.loan.loan_id} - {self.amount} ({self.status})"
