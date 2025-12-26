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
            return Response({
                'message': 'Пароль успешно изменен.'
            }, status=status.HTTP_200_OK)

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
                return Response(
                    {"error": "Refresh token обязателен."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Успешный выход из системы."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": "Неверный токен."},
                status=status.HTTP_400_BAD_REQUEST
            )
