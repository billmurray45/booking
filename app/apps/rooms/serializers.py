from rest_framework import serializers
from datetime import date
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения информации о комнате.
    """
    class Meta:
        model = Room
        fields = [
            'id',
            'room_number',
            'price_per_night',
            'capacity',
            'description',
            'image',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomAvailabilitySerializer(serializers.Serializer):
    """
    Сериализатор для проверки доступности комнат по датам.
    """
    check_in = serializers.DateField(
        required=True,
        help_text='Дата заезда в формате YYYY-MM-DD'
    )
    check_out = serializers.DateField(
        required=True,
        help_text='Дата выезда в формате YYYY-MM-DD'
    )

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
        Проверка что дата выезда позже даты заезда.
        """
        check_in = attrs.get('check_in')
        check_out = attrs.get('check_out')

        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': 'Дата выезда должна быть позже даты заезда.'
            })

        return attrs
