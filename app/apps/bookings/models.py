from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from datetime import date


class Booking(models.Model):
    """
    Модель бронирования.
    """

    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
    ]

    # Связи с другими моделями
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Комната',
        help_text='Забронированная комната'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь',
        help_text='Пользователь, создавший бронирование'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings',
        verbose_name='Кто отменил',
        help_text='Пользователь или администратор, отменивший бронирование'
    )

    # Даты бронирования
    check_in = models.DateField(
        verbose_name='Дата заезда',
        help_text='Дата начала бронирования'
    )
    check_out = models.DateField(
        verbose_name='Дата выезда',
        help_text='Дата окончания бронирования'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Общая стоимость',
        help_text='Автоматически рассчитывается при создании'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус бронирования',
        db_index=True
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отмены',
        help_text='Время отмены бронирования'
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронирование #{self.pk} - {self.room.room_number} ({self.user.username})"

    @property
    def nights_count(self):
        """Количество ночей бронирования."""
        return (self.check_out - self.check_in).days

    @property
    def is_active(self):
        """Проверка, активно ли бронирование."""
        return self.status == 'active'

    @property
    def is_past(self):
        """Проверка, завершилось ли бронирование."""
        return self.check_out < date.today()

    @property
    def is_upcoming(self):
        """Проверка, будущее ли бронирование."""
        return self.check_in > date.today()

    @property
    def is_current(self):
        """Проверка, текущее ли бронирование."""
        today = date.today()
        return self.check_in <= today <= self.check_out

    def clean(self):
        errors = {}

        # Проверка дат
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                errors['check_out'] = 'Дата выезда должна быть позже даты заезда.'

            # Проверка что даты не в прошлом (только для новых объектов)
            if not self.pk:  # Только при создании
                if self.check_in < date.today():
                    errors['check_in'] = 'Дата заезда не может быть в прошлом.'

        if self.room and not self.room.is_active:
            errors['room'] = 'Эта комната недоступна для бронирования.'

        if self.total_price is not None and self.total_price < 0:
            errors['total_price'] = 'Общая стоимость не может быть отрицательной.'

        if self.status == 'cancelled':
            if not self.cancelled_at:
                errors['cancelled_at'] = 'Для отмененного бронирования требуется дата отмены.'
            if not self.cancelled_by:
                errors['cancelled_by'] = 'Для отмененного бронирования требуется информация о том, кто отменил.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
