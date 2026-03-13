from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Role, Permission
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer, PermissionSerializer
from apps.utils.responses import success_response, error_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                {"message": "Usuario registrado exitosamente.", "user": UserSerializer(user).data},
                status=201
            )

        return error_response(
            code="VALIDATION_ERROR",
            message="Error de validación.",
            fields=serializer.errors,
            status=400
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)

        return error_response(
            code="VALIDATION_ERROR",
            message="Error de validación.",
            fields=serializer.errors,
            status=400
        )


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para ver esta lista.",
                status=403
            )

        users = User.objects.all()
        return success_response(UserSerializer(users, many=True).data)


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para ver los roles.",
                status=403
            )

        roles = Role.objects.all()
        return success_response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para crear roles.",
                status=403
            )

        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, status=201)

        return error_response(
            code="VALIDATION_ERROR",
            message="Error de validación.",
            fields=serializer.errors,
            status=400
        )


class RoleAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, role_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para asignar roles.",
                status=403
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return error_response(
                code="MISSING_FIELD",
                message="Se requiere user_id.",
                status=400
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response(code="NOT_FOUND", message="Usuario no encontrado.", status=404)

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return error_response(code="NOT_FOUND", message="Rol no encontrado.", status=404)

        user.roles.add(role)

        return success_response({
            "message": f"Rol '{role.name}' asignado a '{user.email}' exitosamente.",
            "user": UserSerializer(user).data
        })


class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para ver los permisos.",
                status=403
            )

        permissions = Permission.objects.all()
        return success_response(PermissionSerializer(permissions, many=True).data)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return error_response(
                code="PERMISSION_DENIED",
                message="No tenés permisos para crear permisos.",
                status=403
            )

        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, status=201)

        return error_response(
            code="VALIDATION_ERROR",
            message="Error de validación.",
            fields=serializer.errors,
            status=400
        )