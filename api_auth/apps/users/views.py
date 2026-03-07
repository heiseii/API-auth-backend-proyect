from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Role, Permission
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer, PermissionSerializer


# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Usuario registrado exitosamente.",
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Profile View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User List View (solo admin)
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para ver esta lista."},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# Role List View (solo admin)
class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para ver los roles."},
                status=status.HTTP_403_FORBIDDEN
            )

        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para crear roles."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Role Assign View (solo admin)
class RoleAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, role_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para asignar roles."},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "Se requiere user_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {"detail": "Rol no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.roles.add(role)

        return Response(
            {
                "message": f"Rol '{role.name}' asignado a '{user.email}' exitosamente.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )


# Permission List View (solo admin)
class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para ver los permisos."},
                status=status.HTTP_403_FORBIDDEN
            )

        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "No tenés permisos para crear permisos."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)