from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.serializers import UserSerializer
from .serializers import CustomTokenObtainPairSerializer
from .throttles import LoginRateThrottle


# 
# LOGIN VIEW
# 
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")

        # Importamos User acá para evitar imports circulares
        from apps.users.models import User

        # Verificar si el usuario existe y está bloqueado
        try:
            user = User.objects.get(email=email)

            if user.is_locked():
                return Response(
                    {"detail": "Cuenta bloqueada por múltiples intentos fallidos. Intentá más tarde."},
                    status=status.HTTP_403_FORBIDDEN
                )

        except User.DoesNotExist:
            # No revelamos si el usuario existe o no
            pass

        # Intentar autenticación
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Login exitoso — resetear intentos fallidos
            try:
                user = User.objects.get(email=email)
                user.reset_failed_attempts()

                # Guardar IP del usuario
                user.last_login_ip = self._get_client_ip(request)
                user.save(update_fields=["last_login_ip"])

                # Agregar datos del usuario a la respuesta
                response.data["user"] = UserSerializer(user).data

            except User.DoesNotExist:
                pass

        else:
            # Login fallido — registrar intento
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


# 
# LOGOUT VIEW
# 
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"detail": "Se requiere el refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Agregar el token a la blacklist — revocación real
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Sesión cerrada exitosamente."},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"detail": "Token inválido o ya revocado."},
                status=status.HTTP_400_BAD_REQUEST
            )