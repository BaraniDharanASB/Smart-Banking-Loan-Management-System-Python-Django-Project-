from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def loans_root(request):
    """
    Placeholder endpoint for loans API.
    """
    return Response({
        'message': 'Loans API placeholder'
    })
