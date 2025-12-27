from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Room
from .serializers import RoomSerializer, RoomAvailabilitySerializer
from .filters import RoomFilter


@extend_schema(tags=['Rooms'])
@extend_schema_view(
    get=extend_schema(
        summary="Список всех комнат",
        description="Возвращает список всех активных комнат с возможностью фильтрации и сортировки",
    )
)
class RoomListView(generics.ListAPIView):
    """
    Список всех доступных комнат.

    Поддерживает:
    - Фильтрацию по цене (min_price, max_price)
    - Фильтрацию по вместимости (capacity)
    - Сортировку (ordering=price_per_night, -price_per_night, capacity, -capacity)
    - Поиск по номеру комнаты и описанию (search)
    """
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = RoomFilter
    ordering_fields = ['price_per_night', 'capacity', 'room_number']
    ordering = ['room_number']  # сортировка по умолчанию
    search_fields = ['room_number', 'description']


@extend_schema(tags=['Rooms'])
@extend_schema_view(
    get=extend_schema(
        summary="Детали комнаты",
        description="Возвращает подробную информацию о конкретной комнате",
    )
)
class RoomDetailView(generics.RetrieveAPIView):
    """
    Детальная информация о комнате.

    Доступно для всех пользователей без авторизации.
    """
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


@extend_schema(tags=['Rooms'])
class RoomAvailabilityView(APIView):
    """
    Поиск свободных комнат на указанные даты.

    Query параметры:
    - check_in: дата заезда (YYYY-MM-DD)
    - check_out: дата выезда (YYYY-MM-DD)

    Доступно всем пользователям без авторизации.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Поиск свободных комнат",
        description="Возвращает список комнат, доступных для бронирования на указанные даты.",
        parameters=[
            OpenApiParameter(
                name='check_in',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Дата заезда в формате YYYY-MM-DD'
            ),
            OpenApiParameter(
                name='check_out',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Дата выезда в формате YYYY-MM-DD'
            ),
        ],
        responses={200: RoomSerializer(many=True)}
    )
    def get(self, request):
        """
        Получение списка доступных комнат.
        """
        # Валидация входных данных
        serializer = RoomAvailabilitySerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']

        # Получаем доступные комнаты через сервис
        from apps.bookings.services import BookingService
        available_rooms = BookingService.get_available_rooms(check_in, check_out)

        # Сериализуем результат
        room_serializer = RoomSerializer(available_rooms, many=True)

        return Response({
            'check_in': check_in,
            'check_out': check_out,
            'available_rooms_count': available_rooms.count(),
            'available_rooms': room_serializer.data
        }, status=status.HTTP_200_OK)
