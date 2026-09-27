from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def customers_root(request):
    """
    Placeholder endpoint for customers API.
    """
    return Response({
        'message': 'Customers API placeholder'
    })
