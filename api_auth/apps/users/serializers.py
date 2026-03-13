from rest_framework import serializers
from .models import User, Role, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


 
# PERMISSION SERIALIZER
 
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "description"]

#ROLES SERIALIZER       

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permission_ids"]

# REGISTER SERIALIZER
 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password", "password_confirm"]

    def validate_email(self, value):
        value = value.strip().lower()  #aplica minus.
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        value = value.strip()  #elimina espacios
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        default_role = Role.objects.filter(name="user").first()
        if default_role:
            user.roles.add(default_role)

        return user


   
# USER SERIALIZER 

class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "roles", "permissions", "is_active", "created_at", "last_login"
        ]
        read_only_fields = ["id", "email", "is_active", "created_at", "last_login"]

    def get_permissions(self, obj):
        return list(obj.get_all_permissions_codenames())

    def validate_username(self, value):
        return value.strip()

    def validate_first_name(self, value):
        return value.strip().capitalize()

    def validate_last_name(self, value):
        return value.strip().capitalize()