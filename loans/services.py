import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from .models import LoanRepayment

def calculate_emi_details(amount, interest_rate, tenure_months):
    """
    Calculates monthly EMI, total payment, and total interest using Decimal math.
    Formula:
    R = annual_interest_rate / 12 / 100
    N = tenure_months
    P = amount
    If R == 0:
        EMI = P / N
    Else:
        EMI = P * R * (1 + R)^N / ((1 + R)^N - 1)
    """
    P = Decimal(str(amount))
    annual_rate = Decimal(str(interest_rate))
    N = int(tenure_months)

    if annual_rate == Decimal('0.00') or annual_rate == Decimal('0'):
        monthly_emi = (P / Decimal(N)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_payment = P.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_interest = Decimal('0.00')
    else:
        R = annual_rate / Decimal('12') / Decimal('100')
        R_float = float(R)
        compound = (1 + R_float) ** N
        emi_float = float(P) * R_float * compound / (compound - 1)
        monthly_emi = Decimal(str(emi_float)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_payment = (monthly_emi * Decimal(N)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_interest = (total_payment - P).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        'monthly_emi': monthly_emi,
        'total_payment': total_payment,
        'total_interest': total_interest
    }


def generate_repayment_schedule(loan):
    """
    Generates N monthly LoanRepayment records for an approved loan if not already created.
    """
    if LoanRepayment.objects.filter(loan=loan).exists():
        return

    emi_info = calculate_emi_details(loan.amount, loan.interest_rate, loan.tenure_months)
    monthly_emi = emi_info['monthly_emi']

    start_date = loan.approved_date.date() if loan.approved_date else timezone.now().date()

    repayments = []
    for i in range(1, loan.tenure_months + 1):
        year = start_date.year + (start_date.month + i - 1) // 12
        month = (start_date.month + i - 1) % 12 + 1
        day = min(start_date.day, 28)
        due_date = datetime.date(year, month, day)

        repayments.append(
            LoanRepayment(
                repayment_id=LoanRepayment.generate_unique_repayment_id(),
                loan=loan,
                installment_number=i,
                due_date=due_date,
                amount=monthly_emi,
                status=LoanRepayment.RepaymentStatus.PENDING
            )
        )

    LoanRepayment.objects.bulk_create(repayments)
