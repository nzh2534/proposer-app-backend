from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView

class InitialLoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

class BlacklistTokenUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)