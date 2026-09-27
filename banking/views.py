from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from customers.models import Customer
from .models import BankAccount
from .serializers import BankAccountSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def account_list_create(request):
    """
    GET: List bank accounts.
         - Admin/Employee users can view all bank accounts.
         - Customer users can view only their own bank accounts.
    POST: Create a new bank account for the authenticated user's customer profile.
    """
    user = request.user

    if request.method == 'GET':
        if user.role in ['ADMIN', 'EMPLOYEE'] or user.is_staff:
            accounts = BankAccount.objects.all()
        else:
            try:
                customer = user.customer_profile
                accounts = BankAccount.objects.filter(customer=customer)
            except Customer.DoesNotExist:
                return Response(
                    {'detail': 'Customer profile not found. Please create a customer profile first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found. Please create a customer profile first before opening a bank account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                customer=customer,
                balance=0,
                status=BankAccount.AccountStatus.ACTIVE
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_detail(request, pk):
    """
    GET: Retrieve specific bank account details by ID.
         - Admin/Employee users can view any bank account.
         - Customer users can view only their own bank account.
    """
    user = request.user
    try:
        account = BankAccount.objects.get(pk=pk)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        try:
            customer = user.customer_profile
            if account.customer != customer:
                return Response(
                    {'detail': 'You do not have permission to view this account.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found.'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = BankAccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_200_OK)
