from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.utils.responses import error_response, success_response
from apps.users.serializers import UserSerializer
from .serializers import CustomTokenObtainPairSerializer
from .throttles import LoginRateThrottle


 
# LOGIN VIEW
 
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")

        from apps.users.models import User

        try:
            user = User.objects.get(email=email)

            if user.is_locked():
                return Response(
                    {"detail": "Cuenta bloqueada por múltiples intentos fallidos. Intentá más tarde."},
                    status=status.HTTP_403_FORBIDDEN
                )

        except User.DoesNotExist:
            pass

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            try:
                user = User.objects.get(email=email)
                user.reset_failed_attempts()

                user.last_login_ip = self._get_client_ip(request) #guardar ip
                user.save(update_fields=["last_login_ip"])

                response.data["user"] = UserSerializer(user).data #guardar passw

            except User.DoesNotExist:
                pass

        else:
            try:
                user = User.objects.get(email=email)
                user.register_failed_attempt(
                    max_attempts=settings.MAX_FAILED_ATTEMPTS,
                    lockout_minutes=settings.LOCKOUT_DURATION_MINUTES
                )
            except User.DoesNotExist:
                pass

        return response

    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")



# LOGOUT VIEW

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error_response(
                code="MISSING_FIELD",
                message="Se requiere el refresh token.",
                status=400
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response({"message": "Sesión cerrada exitosamente."})

        except TokenError:
            return error_response(
                code="INVALID_TOKEN",
                message="Token inválido o ya revocado.",
                status=400
            )