from django.contrib import admin
from django.utils.html import format_html
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Административная панель для управления комнатами.
    """
    list_display = [
        'room_number',
        'image_preview',
        'price_per_night',
        'capacity',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'capacity',
        'created_at'
    ]
    search_fields = [
        'room_number',
        'description'
    ]
    ordering = ['room_number']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('room_number', 'price_per_night', 'capacity')
        }),
        ('Дополнительно', {
            'fields': ('description', 'image', 'image_preview_large', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        """
        Превью изображения в списке (маленькое).
        """
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Фото'

    def image_preview_large(self, obj):
        """
        Превью изображения на странице редактирования (большое).
        """
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return 'Изображение не загружено'
    image_preview_large.short_description = 'Текущее изображение'

    def get_queryset(self, request):
        """
        Оптимизация запросов.
        """
        qs = super().get_queryset(request)
        return qs.select_related()
