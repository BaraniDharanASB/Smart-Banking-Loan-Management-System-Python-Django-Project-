from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def auth_root(request):
    """
    Placeholder endpoint for authentication API root.
    """
    return Response({
        'message': 'Auth API placeholder',
        'endpoints': {
            'token_obtain': '/api/auth/token/',
            'token_refresh': '/api/auth/token/refresh/'
        }
    })
