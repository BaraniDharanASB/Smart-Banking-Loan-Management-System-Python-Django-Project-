from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from customers.models import Customer
from .models import Loan
from .serializers import (
    LoanApplicationSerializer,
    LoanRejectSerializer,
    LoanDetailSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loan_list_create(request):
    """
    GET: List loans.
         - Admin/Employee users can view all loans.
         - Customer users can view only their own loans.
    POST: Apply for a new loan.
         - Authenticated customer applies for a loan.
    """
    user = request.user

    if request.method == 'GET':
        if user.role in ['ADMIN', 'EMPLOYEE'] or user.is_staff:
            loans = Loan.objects.all().order_by('-application_date')
        else:
            try:
                customer = user.customer_profile
                loans = Loan.objects.filter(customer=customer).order_by('-application_date')
            except Customer.DoesNotExist:
                return Response(
                    {'detail': 'Customer profile not found. Please create a customer profile first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found. Please create a customer profile first before applying for a loan.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save(
                customer=customer,
                status=Loan.LoanStatus.PENDING
            )
            return Response(LoanDetailSerializer(loan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_detail(request, pk):
    """
    GET: Retrieve specific loan details by ID.
         - Admin/Employee users can view any loan.
         - Customer users can view only their own loan.
    """
    user = request.user
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        try:
            customer = user.customer_profile
            if loan.customer != customer:
                return Response(
                    {'detail': 'You do not have permission to view this loan.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found.'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_approve(request, pk):
    """
    POST: Approve a pending loan application.
          - Only EMPLOYEE or ADMIN users can approve loans.
          - Only PENDING loans can be approved.
    """
    user = request.user

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        return Response(
            {'detail': 'You do not have permission to approve loans.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)

    if loan.status != Loan.LoanStatus.PENDING:
        return Response(
            {'detail': f'Cannot approve loan with status {loan.status}. Only PENDING loans can be approved.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    loan.status = Loan.LoanStatus.APPROVED
    loan.approved_date = timezone.now()
    loan.save()

    return Response({
        'message': 'Loan approved successfully',
        'loan': LoanDetailSerializer(loan).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_reject(request, pk):
    """
    POST: Reject a pending loan application.
          - Only EMPLOYEE or ADMIN users can reject loans.
          - Only PENDING loans can be rejected.
          - Requires rejection_reason.
    """
    user = request.user

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        return Response(
            {'detail': 'You do not have permission to reject loans.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response({'detail': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)

    if loan.status != Loan.LoanStatus.PENDING:
        return Response(
            {'detail': f'Cannot reject loan with status {loan.status}. Only PENDING loans can be rejected.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = LoanRejectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    rejection_reason = serializer.validated_data['rejection_reason']
    loan.status = Loan.LoanStatus.REJECTED
    loan.rejection_reason = rejection_reason
    loan.save()

    return Response({
        'message': 'Loan rejected successfully',
        'loan': LoanDetailSerializer(loan).data
    }, status=status.HTTP_200_OK)
