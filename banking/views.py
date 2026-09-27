from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from customers.models import Customer
from .models import BankAccount, Transaction
from .serializers import (
    BankAccountSerializer,
    DepositSerializer,
    WithdrawSerializer,
    TransferSerializer,
    TransactionSerializer
)

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
                balance=Decimal('0.00'),
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_view(request):
    """
    POST: Deposit funds into a bank account.
    """
    user = request.user
    serializer = DepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    account_id = serializer.validated_data['account_id']
    amount = serializer.validated_data['amount']
    description = serializer.validated_data.get('description', 'Cash deposit')

    try:
        account = BankAccount.objects.get(pk=account_id)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        try:
            customer = user.customer_profile
            if account.customer != customer:
                return Response({'detail': 'You do not have permission to operate on this account.'}, status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            return Response({'detail': 'Customer profile not found.'}, status=status.HTTP_403_FORBIDDEN)

    if account.status != BankAccount.AccountStatus.ACTIVE:
        return Response({'detail': 'Only active accounts can perform transactions.'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        account.balance += amount
        account.save()

        txn = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.DEPOSIT,
            destination_account=account,
            amount=amount,
            status=Transaction.TransactionStatus.SUCCESS,
            description=description
        )

    return Response({
        'message': 'Deposit successful',
        'account_id': account.id,
        'account_number': account.account_number,
        'new_balance': account.balance,
        'transaction': TransactionSerializer(txn).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_view(request):
    """
    POST: Withdraw funds from a bank account.
    """
    user = request.user
    serializer = WithdrawSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    account_id = serializer.validated_data['account_id']
    amount = serializer.validated_data['amount']
    description = serializer.validated_data.get('description', 'Cash withdrawal')

    try:
        account = BankAccount.objects.get(pk=account_id)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        try:
            customer = user.customer_profile
            if account.customer != customer:
                return Response({'detail': 'You do not have permission to operate on this account.'}, status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            return Response({'detail': 'Customer profile not found.'}, status=status.HTTP_403_FORBIDDEN)

    if account.status != BankAccount.AccountStatus.ACTIVE:
        return Response({'detail': 'Only active accounts can perform transactions.'}, status=status.HTTP_400_BAD_REQUEST)

    if account.balance < amount:
        return Response({'detail': 'Insufficient balance for withdrawal.'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        account.balance -= amount
        account.save()

        txn = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            source_account=account,
            amount=amount,
            status=Transaction.TransactionStatus.SUCCESS,
            description=description
        )

    return Response({
        'message': 'Withdrawal successful',
        'account_id': account.id,
        'account_number': account.account_number,
        'new_balance': account.balance,
        'transaction': TransactionSerializer(txn).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_view(request):
    """
    POST: Transfer funds from source_account to destination_account atomically.
    """
    user = request.user
    serializer = TransferSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    source_account_id = serializer.validated_data['source_account_id']
    destination_account_id = serializer.validated_data['destination_account_id']
    amount = serializer.validated_data['amount']
    description = serializer.validated_data.get('description', 'Fund transfer')

    try:
        source_account = BankAccount.objects.get(pk=source_account_id)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Source bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        destination_account = BankAccount.objects.get(pk=destination_account_id)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Destination bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role not in ['ADMIN', 'EMPLOYEE'] and not user.is_staff:
        try:
            customer = user.customer_profile
            if source_account.customer != customer:
                return Response({'detail': 'You do not have permission to transfer from this account.'}, status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            return Response({'detail': 'Customer profile not found.'}, status=status.HTTP_403_FORBIDDEN)

    if source_account.status != BankAccount.AccountStatus.ACTIVE:
        return Response({'detail': 'Source account is not active.'}, status=status.HTTP_400_BAD_REQUEST)

    if destination_account.status != BankAccount.AccountStatus.ACTIVE:
        return Response({'detail': 'Destination account is not active.'}, status=status.HTTP_400_BAD_REQUEST)

    if source_account.balance < amount:
        return Response({'detail': 'Insufficient balance for transfer.'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        source_account.balance -= amount
        source_account.save()

        destination_account.balance += amount
        destination_account.save()

        txn = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.TRANSFER,
            source_account=source_account,
            destination_account=destination_account,
            amount=amount,
            status=Transaction.TransactionStatus.SUCCESS,
            description=description
        )

    return Response({
        'message': 'Fund transfer successful',
        'source_account_id': source_account.id,
        'source_account_number': source_account.account_number,
        'source_new_balance': source_account.balance,
        'destination_account_id': destination_account.id,
        'destination_account_number': destination_account.account_number,
        'transaction': TransactionSerializer(txn).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    """
    GET: List transaction history.
         - Admin/Employee users can view all transaction history.
         - Customer users can view transactions involving their accounts.
    """
    user = request.user

    if user.role in ['ADMIN', 'EMPLOYEE'] or user.is_staff:
        transactions = Transaction.objects.all().order_by('-transaction_date')
    else:
        try:
            customer = user.customer_profile
            transactions = Transaction.objects.filter(
                Q(source_account__customer=customer) | Q(destination_account__customer=customer)
            ).distinct().order_by('-transaction_date')
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
