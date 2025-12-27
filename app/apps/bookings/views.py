import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Booking
from .serializers import (
    BookingSerializer,
    BookingListSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
)
from .permissions import IsOwnerOrAdmin
from .services import BookingService
from .filters import BookingFilter

logger = logging.getLogger(__name__)


@extend_schema(tags=['Bookings'])
@extend_schema_view(
    post=extend_schema(
        summary="Создать бронирование",
        description="Создание нового бронирования комнаты.",
        request=BookingCreateSerializer,
        responses={201: BookingSerializer}
    )
)
class BookingCreateView(generics.CreateAPIView):
    """ Создание нового бронирования. """
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        output_serializer = BookingSerializer(booking)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Bookings'])
@extend_schema_view(
    get=extend_schema(
        summary="Список своих бронирований",
        description="Получение списка бронирований текущего пользователя с фильтрацией и сортировкой.",
    )
)
class BookingListView(generics.ListAPIView):
    """
    Список бронирований текущего пользователя.

    Поддерживает:
    - Фильтрацию по статусу (status=active|cancelled)
    - Фильтрацию по датам (check_in_after, check_out_before)
    - Сортировку (ordering=-created_at, check_in, -check_in, etc.)
    """
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['created_at', 'check_in', 'check_out', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Возвращает только бронирования текущего пользователя.
        Администраторы видят все бронирования.
        """
        user = self.request.user

        queryset = Booking.objects.select_related('room', 'user')

        if not (user.is_staff or user.is_superuser):
            queryset = queryset.filter(user=user)

        return queryset


@extend_schema(tags=['Bookings'])
@extend_schema_view(
    get=extend_schema(
        summary="Детали бронирования",
        description="Получение подробной информации о конкретном бронировании. Доступно только владельцу или администратору.",
    )
)
class BookingDetailView(generics.RetrieveAPIView):
    """Информация о бронировании."""
    queryset = Booking.objects.select_related('room', 'user', 'cancelled_by')
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'pk'


@extend_schema(tags=['Bookings'])
@extend_schema_view(
    patch=extend_schema(
        summary="Изменить даты бронирования",
        description="Обновление дат существующего бронирования. Доступно только владельцу или администратору. Только для активных бронирований.",
        request=BookingUpdateSerializer,
        responses={200: BookingSerializer}
    ),
    put=extend_schema(
        summary="Изменить даты бронирования (полное обновление)",
        description="Полное обновление дат бронирования.",
        request=BookingUpdateSerializer,
        responses={200: BookingSerializer}
    )
)
class BookingUpdateView(generics.UpdateAPIView):
    """
    Обновление дат бронирования.

    Требования:
    - Доступно только владельцу или администратору
    - Бронирование должно быть активным
    - Новые даты не должны конфликтовать с другими бронированиями
    """
    queryset = Booking.objects.all()
    serializer_class = BookingUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'pk'
    http_method_names = ['patch', 'put']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        output_serializer = BookingSerializer(booking)

        return Response(output_serializer.data)


@extend_schema(tags=['Bookings'])
class BookingCancelView(APIView):
    """
    Отмена (мягкое удаление) бронирования.

    При отмене:
    - status меняется на 'cancelled'
    - сохраняется cancelled_by (кто отменил)
    - сохраняется cancelled_at (когда отменено)
    - данные остаются в БД для истории
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    @extend_schema(
        summary="Отменить бронирование",
        description="Мягкое удаление бронирования. Доступно только владельцу или администратору.",
        responses={200: BookingSerializer}
    )
    def delete(self, request, pk):
        try:
            booking = Booking.objects.select_related('room', 'user').get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Бронирование не найдено.'},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, booking)

        # Отмена через сервис
        try:
            cancelled_booking = BookingService.cancel_booking(
                booking=booking,
                cancelled_by=request.user
            )

            serializer = BookingSerializer(cancelled_booking)

            return Response({
                'message': 'Бронирование успешно отменено.',
                'booking': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error cancelling booking {pk} by user {request.user.username}: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
