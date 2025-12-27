import logging
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from typing import Optional, Tuple

from apps.rooms.models import Room
from .models import Booking

logger = logging.getLogger(__name__)


class BookingService: # Сервис для отмена бронирование

    @staticmethod
    def calculate_total_price(room: Room, check_in: date, check_out: date) -> Decimal:
        """
        Расчет общей стоимости бронирования.

        Args:
            room: Комната для бронирования
            check_in: Дата заезда
            check_out: Дата выезда

        Returns:
            Decimal: Общая стоимость
        """
        nights = (check_out - check_in).days
        if nights <= 0:
            raise ValidationError("Количество ночей должно быть больше 0")

        return room.price_per_night * nights

    @staticmethod
    def check_room_availability(
        room: Room,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Проверка доступности комнаты на указанные даты.
        """
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status='active'
        ).filter(
            # Алгоритм проверки пересечения дат
            Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        )

        # Исключаем текущее бронирование при редактировании
        if exclude_booking_id:
            conflicting_bookings = conflicting_bookings.exclude(id=exclude_booking_id)

        if conflicting_bookings.exists():
            first_conflict = conflicting_bookings.first()
            error_msg = (
                f"Комната {room.room_number} уже забронирована на эти даты. "
                f"Конфликтующее бронирование: с {first_conflict.check_in} по {first_conflict.check_out}"
            )
            return False, error_msg

        return True, None

    @staticmethod
    @transaction.atomic
    def create_booking(
        user,
        room: Room,
        check_in: date,
        check_out: date
    ) -> Booking:
        """
        Создание нового бронирования.
        """
        room = Room.objects.select_for_update().get(pk=room.pk)

        # Проверяем доступность
        is_available, error_msg = BookingService.check_room_availability(
            room, check_in, check_out
        )

        if not is_available:
            logger.warning(f'Booking creation failed - room unavailable: Room {room.room_number}, {check_in} to {check_out}, User: {user.username}')
            raise ValidationError({'room': error_msg})

        # Рассчитываем стоимость
        total_price = BookingService.calculate_total_price(room, check_in, check_out)

        # Создаем бронирование
        booking = Booking.objects.create(
            user=user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status='active'
        )

        logger.info(f'Booking created: ID {booking.id}, Room {room.room_number}, User: {user.username}, Dates: {check_in} to {check_out}, Price: {total_price}')

        return booking

    @staticmethod
    @transaction.atomic
    def update_booking_dates(
        booking: Booking,
        check_in: date,
        check_out: date
    ) -> Booking:
        """
        Обновление дат существующего бронирования с проверкой доступности.
        """
        # Проверяем что бронирование активно
        if booking.status != 'active':
            raise ValidationError("Нельзя редактировать отмененное бронирование")

        # Блокируем комнату
        room = Room.objects.select_for_update().get(pk=booking.room.pk)

        # Проверяем доступность (исключая текущее бронирование)
        is_available, error_msg = BookingService.check_room_availability(
            room, check_in, check_out, exclude_booking_id=booking.id
        )

        if not is_available:
            logger.warning(f'Booking update failed - room unavailable: Booking ID {booking.id}, Room {room.room_number}, New dates: {check_in} to {check_out}')
            raise ValidationError({'dates': error_msg})

        # Обновляем даты и пересчитываем стоимость
        old_check_in = booking.check_in
        old_check_out = booking.check_out
        old_price = booking.total_price

        booking.check_in = check_in
        booking.check_out = check_out
        booking.total_price = BookingService.calculate_total_price(
            room, check_in, check_out
        )
        booking.save()

        logger.info(f'Booking updated: ID {booking.id}, Room {room.room_number}, Old dates: {old_check_in} to {old_check_out}, New dates: {check_in} to {check_out}, Price: {old_price} -> {booking.total_price}')

        return booking

    @staticmethod
    def cancel_booking(booking: Booking, cancelled_by) -> Booking:
        """
        Мягкое удаление (отмена) бронирования.
        """
        if booking.status == 'cancelled':
            logger.warning(f'Attempt to cancel already cancelled booking: ID {booking.id}')
            raise ValidationError("Бронирование уже отменено")

        from django.utils import timezone

        booking.status = 'cancelled'
        booking.cancelled_by = cancelled_by
        booking.cancelled_at = timezone.now()
        booking.save()

        logger.info(f'Booking cancelled: ID {booking.id}, Room {booking.room.room_number}, User: {booking.user.username}, Cancelled by: {cancelled_by.username}, Dates: {booking.check_in} to {booking.check_out}')

        return booking

    @staticmethod
    def get_available_rooms(check_in: date, check_out: date):
        """
        Получение списка доступных комнат на указанные даты.
        """
        conflicting_bookings = Booking.objects.filter(
            room=OuterRef('pk'),
            status='active'
        ).filter(
            Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        )

        available_rooms = Room.objects.filter(
            is_active=True
        ).exclude(
            Exists(conflicting_bookings)
        )

        return available_rooms
