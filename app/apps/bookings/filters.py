import django_filters
from datetime import date
from .models import Booking


class BookingFilter(django_filters.FilterSet):
    """
    Фильтр для бронирований.

    Поддерживаемые фильтры:
    - status: точное совпадение (active/cancelled)
    - check_in_after: дата заезда >= указанной
    - check_in_before: дата заезда <= указанной
    - check_out_after: дата выезда >= указанной
    - check_out_before: дата выезда <= указанной
    - is_past: завершенные бронирования
    - is_upcoming: будущие бронирования
    - is_current: текущие бронирования
    """

    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=Booking.STATUS_CHOICES,
        label='Статус бронирования'
    )

    check_in_after = django_filters.DateFilter(
        field_name='check_in',
        lookup_expr='gte',
        label='Дата заезда от'
    )

    check_in_before = django_filters.DateFilter(
        field_name='check_in',
        lookup_expr='lte',
        label='Дата заезда до'
    )

    check_out_after = django_filters.DateFilter(
        field_name='check_out',
        lookup_expr='gte',
        label='Дата выезда от'
    )

    check_out_before = django_filters.DateFilter(
        field_name='check_out',
        lookup_expr='lte',
        label='Дата выезда до'
    )

    # Булевы фильтры для удобства
    is_past = django_filters.BooleanFilter(
        method='filter_is_past',
        label='Завершенные бронирования'
    )

    is_upcoming = django_filters.BooleanFilter(
        method='filter_is_upcoming',
        label='Будущие бронирования'
    )

    is_current = django_filters.BooleanFilter(
        method='filter_is_current',
        label='Текущие бронирования'
    )

    def filter_is_past(self, queryset, name, value):
        if value:
            return queryset.filter(check_out__lt=date.today())
        return queryset.exclude(check_out__lt=date.today())

    def filter_is_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(check_in__gt=date.today())
        return queryset.exclude(check_in__gt=date.today())

    def filter_is_current(self, queryset, name, value):
        today = date.today()
        if value:
            return queryset.filter(check_in__lte=today, check_out__gte=today)
        return queryset.exclude(check_in__lte=today, check_out__gte=today)

    class Meta:
        model = Booking
        fields = [
            'status',
            'check_in_after',
            'check_in_before',
            'check_out_after',
            'check_out_before',
            'is_past',
            'is_upcoming',
            'is_current',
        ]
