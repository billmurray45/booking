from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомное разрешение: только владелец бронирования или администратор.

    Используется для:
    - Просмотра деталей бронирования
    - Редактирования дат
    - Отмены бронирования
    """

    message = 'Доступ разрешен только владельцу бронирования или администратору.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.user == request.user
