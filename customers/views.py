from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerProfileSerializer

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def customer_profile(request):
    """
    API endpoint for customer profile creation, retrieval, and updating.
    - POST: Create profile for the authenticated user.
    - GET: Retrieve profile of the authenticated user.
    - PUT: Update profile of the authenticated user.
    """
    user = request.user

    if request.method == 'GET':
        try:
            profile = user.customer_profile
            serializer = CustomerProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    elif request.method == 'POST':
        if hasattr(user, 'customer_profile'):
            return Response(
                {'detail': 'Customer profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        try:
            profile = user.customer_profile
        except Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer profile not found. Please create one first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
