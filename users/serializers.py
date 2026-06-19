from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'position', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации с паролем"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'position', 'role', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            position=validated_data.get('position', 'Сотрудник'),
            role=validated_data.get('role', 'employee')
        )
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников (CRUD)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'position', 'role']
        read_only_fields = ['role']

    def validate_full_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("ФИО должно содержать минимум 2 символа")
        return value.strip()

    def validate_position(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Должность должна содержать минимум 2 символа")
        return value.strip()


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания сотрудника (только для менеджера)"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'position', 'role', 'password']
        read_only_fields = ['role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            position=validated_data.get('position', 'Сотрудник'),
            role='employee'  # Всегда создаём как сотрудника
        )
        return user