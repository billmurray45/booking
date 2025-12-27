from rest_framework import serializers
from datetime import date
from decimal import Decimal

from .models import Booking
from .services import BookingService
from apps.rooms.models import Room
from apps.rooms.serializers import RoomSerializer
from apps.users.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о бронировании.
    """
    room = RoomSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    cancelled_by = UserSerializer(read_only=True)
    nights_count = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'room',
            'user',
            'check_in',
            'check_out',
            'total_price',
            'status',
            'cancelled_by',
            'cancelled_at',
            'created_at',
            'updated_at',

            'nights_count',
            'is_active',
            'is_past',
            'is_upcoming',
            'is_current',
        ]
        read_only_fields = [
            'id', 'user', 'total_price', 'status',
            'cancelled_by', 'cancelled_at',
            'created_at', 'updated_at'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """
    Облегченный сериализатор для списка бронирований.
    """
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_price = serializers.DecimalField(
        source='room.price_per_night',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    nights_count = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'room_number',
            'room_price',
            'check_in',
            'check_out',
            'nights_count',
            'total_price',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'total_price', 'status', 'created_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания бронирования.
    Валидирует даты и проверяет доступность комнаты.
    """
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True),
        help_text='ID комнаты для бронирования'
    )

    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out']

    def validate_check_in(self, value):
        """
        Проверка что дата заезда не в прошлом.
        """
        if value < date.today():
            raise serializers.ValidationError(
                "Дата заезда не может быть в прошлом."
            )
        return value

    def validate(self, attrs):
        """
        Комплексная валидация дат и доступности.
        """
        check_in = attrs.get('check_in')
        check_out = attrs.get('check_out')
        room = attrs.get('room')

        # Проверка что check_out > check_in
        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': 'Дата выезда должна быть позже даты заезда.'
            })

        # Проверка разумности периода (например, не более 365 дней)
        days_diff = (check_out - check_in).days
        if days_diff > 365:
            raise serializers.ValidationError({
                'check_out': 'Максимальный период бронирования - 365 дней.'
            })

        # Проверка доступности комнаты
        is_available, error_msg = BookingService.check_room_availability(
            room, check_in, check_out
        )

        if not is_available:
            raise serializers.ValidationError({
                'room': error_msg
            })

        return attrs

    def create(self, validated_data):
        """
        Создание бронирования через сервисный слой.
        """
        user = self.context['request'].user
        room = validated_data['room']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']

        # Используем сервис для создания
        booking = BookingService.create_booking(
            user=user,
            room=room,
            check_in=check_in,
            check_out=check_out
        )

        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления дат бронирования.
    Только владелец или админ может обновлять.
    """

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']

    def validate_check_in(self, value):
        """
        Проверка что новая дата заезда не в прошлом.
        """
        if value < date.today():
            raise serializers.ValidationError(
                "Дата заезда не может быть в прошлом."
            )
        return value

    def validate(self, attrs):
        """
        Валидация новых дат и проверка доступности.
        """
        # Получаем текущий объект
        instance = self.instance

        # Проверяем что бронирование активно
        if instance.status != 'active':
            raise serializers.ValidationError(
                "Нельзя редактировать отмененное бронирование."
            )

        # Получаем новые даты (или используем существующие)
        check_in = attrs.get('check_in', instance.check_in)
        check_out = attrs.get('check_out', instance.check_out)

        # Проверка что check_out > check_in
        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': 'Дата выезда должна быть позже даты заезда.'
            })

        # Проверка разумности периода
        days_diff = (check_out - check_in).days
        if days_diff > 365:
            raise serializers.ValidationError({
                'check_out': 'Максимальный период бронирования - 365 дней.'
            })

        # Проверка доступности (исключая текущее бронирование)
        is_available, error_msg = BookingService.check_room_availability(
            instance.room, check_in, check_out, exclude_booking_id=instance.id
        )

        if not is_available:
            raise serializers.ValidationError({
                'dates': error_msg
            })

        return attrs

    def update(self, instance, validated_data):
        """
        Обновление дат через сервисный слой.
        """
        check_in = validated_data.get('check_in', instance.check_in)
        check_out = validated_data.get('check_out', instance.check_out)

        # Используем сервис для обновления (с транзакцией)
        booking = BookingService.update_booking_dates(
            booking=instance,
            check_in=check_in,
            check_out=check_out
        )

        return booking
