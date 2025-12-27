import logging
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)

logger = logging.getLogger(__name__)


@extend_schema(tags=['Authentication'])
class UserRegistrationView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерация JWT токенов для нового пользователя
        refresh = RefreshToken.for_user(user)

        logger.info(f'New user registered: {user.username} (ID: {user.id}, Email: {user.email})')

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['User Profile'])
@extend_schema_view(
    get=extend_schema(
        summary="Получить информацию о текущем пользователе",
        description="Возвращает данные авторизованного пользователя"
    ),
    patch=extend_schema(
        summary="Обновить профиль",
        description="Обновление данных профиля пользователя"
    ),
    put=extend_schema(
        summary="Обновить профиль (полное)",
        description="Полное обновление данных профиля"
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление профиля текущего пользователя.

    GET - получить информацию о себе
    PATCH - частичное обновление профиля
    PUT - полное обновление профиля
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Возвращает текущего авторизованного пользователя.
        """
        return self.request.user

    def get_serializer_class(self):
        """
        Использовать разные сериализаторы для GET и PUT/PATCH.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        """
        Обновление профиля с логированием.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        logger.info(f'User profile updated: {instance.username} (ID: {instance.id})')

        return Response(UserSerializer(instance).data)


@extend_schema(tags=['User Profile'])
class ChangePasswordView(APIView):
    """
    Смена пароля для текущего пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: {'description': 'Пароль успешно изменен'}},
        summary="Сменить пароль",
        description="Смена пароля авторизованного пользователя"
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            logger.info(f'Password changed for user: {request.user.username} (ID: {request.user.id})')
            return Response({
                'message': 'Пароль успешно изменен.'
            }, status=status.HTTP_200_OK)

        logger.warning(f'Failed password change attempt for user: {request.user.username} (ID: {request.user.id})')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    """
    Выход из системы (logout).

    Добавляет refresh токен в черный список.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string'}
                },
                'required': ['refresh']
            }
        },
        responses={205: {'description': 'Успешный выход из системы'}},
        summary="Выход из системы",
        description="Инвалидация refresh токена"
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                logger.warning(f'Logout attempt without refresh token from user: {request.user.username}')
                return Response(
                    {"error": "Refresh token обязателен."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f'User logged out: {request.user.username} (ID: {request.user.id})')

            return Response(
                {"message": "Успешный выход из системы."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            logger.error(f'Logout error for user {request.user.username}: {str(e)}')
            return Response(
                {"error": "Неверный токен."},
                status=status.HTTP_400_BAD_REQUEST
            )
