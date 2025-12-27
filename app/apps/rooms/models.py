from django.db import models
from django.core.exceptions import ValidationError


class Room(models.Model):
    room_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Номер комнаты',
        help_text='Уникальный номер или название комнаты'
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за ночь',
        help_text='Стоимость проживания за одну ночь'
    )
    capacity = models.PositiveIntegerField(
        verbose_name='Вместимость',
        help_text='Количество мест в комнате'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Подробное описание комнаты и удобств'
    )
    image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Фотография комнаты'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Доступна ли комната для бронирования'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        db_table = 'rooms'
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering = ['room_number']

    def __str__(self):
        return f"Комната {self.room_number}"

    def clean(self):
        if self.price_per_night is not None and self.price_per_night <= 0:
            raise ValidationError({
                'price_per_night': 'Цена за ночь должна быть больше 0'
            })

        if self.capacity is not None and self.capacity <= 0:
            raise ValidationError({
                'capacity': 'Вместимость должна быть больше 0'
            })

        if self.capacity is not None and self.capacity > 20:
            raise ValidationError({
                'capacity': 'Вместимость не может превышать 20 человек'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
