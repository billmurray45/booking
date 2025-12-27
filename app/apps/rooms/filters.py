import django_filters
from .models import Room


class RoomFilter(django_filters.FilterSet):
    """
    Фильтр для комнат отеля.
    Поддерживает фильтрацию по диапазону цен и вместимости.
    """
    min_price = django_filters.NumberFilter(
        field_name='price_per_night',
        lookup_expr='gte',
        label='Минимальная цена'
    )
    max_price = django_filters.NumberFilter(
        field_name='price_per_night',
        lookup_expr='lte',
        label='Максимальная цена'
    )
    capacity = django_filters.NumberFilter(
        field_name='capacity',
        lookup_expr='exact',
        label='Вместимость (точное совпадение)'
    )
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Активна'
    )

    class Meta:
        model = Room
        fields = ['min_price', 'max_price', 'capacity', 'is_active']
