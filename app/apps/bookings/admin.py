from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'get_room_link',
        'get_user_link',
        'check_in',
        'check_out',
        'get_nights_count',
        'total_price',
        'get_status_badge',
        'created_at',
    ]

    list_filter = [
        'status',
        'created_at',
        'check_in',
        'check_out',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'room__room_number',
        'id',
    ]

    readonly_fields = [
        'total_price',
        'created_at',
        'updated_at',
        'get_nights_count',
        'cancelled_at',
    ]

    autocomplete_fields = [
        'room',
        'user',
        'cancelled_by',
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('room', 'user', 'status')
        }),
        ('Даты бронирования', {
            'fields': ('check_in', 'check_out', 'get_nights_count')
        }),
        ('Финансы', {
            'fields': ('total_price',)
        }),
        ('Информация об отмене', {
            'fields': ('cancelled_by', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['-created_at']

    list_per_page = 25

    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        """
        Оптимизация запросов через select_related.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('room', 'user', 'cancelled_by')

    def get_room_link(self, obj):
        if obj.room:
            url = reverse('admin:rooms_room_change', args=[obj.room.pk])
            return format_html('<a href="{}">{}</a>', url, obj.room.room_number)
        return '-'
    get_room_link.short_description = 'Комната'
    get_room_link.admin_order_field = 'room__room_number'

    def get_user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    get_user_link.short_description = 'Пользователь'
    get_user_link.admin_order_field = 'user__username'

    def get_status_badge(self, obj):
        if obj.status == 'active':
            color = '#28a745'
            text = 'Активно'
        elif obj.status == 'cancelled':
            color = '#dc3545'
            text = 'Отменено'
        else:
            color = '#6c757d'
            text = obj.status

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            text
        )
    get_status_badge.short_description = 'Статус'
    get_status_badge.admin_order_field = 'status'

    def get_nights_count(self, obj):
        """
        Количество ночей бронирования.
        """
        return obj.nights_count
    get_nights_count.short_description = 'Количество ночей'

    def has_delete_permission(self, request, obj=None):
        return False
