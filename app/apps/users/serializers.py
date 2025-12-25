import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer): # Сериализатор для вывода информации про пользователя
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'date_joined',
            'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer): # Сериализатор для создание пользователя
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False}
        }

    def validate_email(self, value): # Валидация почты
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_username(self, value): # Валидация username
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")

        if len(value) < 3:
            raise serializers.ValidationError("Username должен содержать минимум 3 символа.")

        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError(
                "Username может содержать только буквы, цифры, _ и -"
            )

        reserved_names = ['admin', 'root', 'superuser', 'user', 'api', 'system']
        if value.lower() in reserved_names:
            raise serializers.ValidationError("Этот username зарезервирован системой.")

        return value

    def validate_phone(self, value): # Валидация номера телефона
        if value:
            cleaned = re.sub(r'[^\d+]', '', value)

            if not re.match(r'^\+\d{10,15}$', cleaned):
                raise serializers.ValidationError(
                    "Неверный формат телефона. Используйте международный формат: +7XXXXXXXXXX"
                )
            return cleaned
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', '')
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer): # Сериализатор для обновление пользователя

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone'
        ]

    def validate_email(self, value):
        user = self.context['request'].user

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "Этот email уже используется другим пользователем."
            )
        return value

    def validate_phone(self, value): # Валидация телефона
        if value:
            cleaned = re.sub(r'[^\d+]', '', value)

            if not re.match(r'^\+\d{10,15}$', cleaned):
                raise serializers.ValidationError(
                    "Неверный формат телефона. Используйте международный формат: +7XXXXXXXXXX"
                )
            return cleaned
        return value


class ChangePasswordSerializer(serializers.Serializer): # Сериализатор для смены пароля
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный старый пароль.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Новые пароли не совпадают."
            })

        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                "new_password": "Новый пароль не должен совпадать со старым."
            })

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
