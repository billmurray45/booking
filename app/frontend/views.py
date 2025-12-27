from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    """
    Главная страница приложения.
    """
    template_name = 'index.html'


class RegisterView(TemplateView):
    """
    Страница регистрации нового пользователя.
    """
    template_name = 'register.html'


class LoginView(TemplateView):
    """
    Страница входа в систему.
    """
    template_name = 'login.html'


class ProfileView(TemplateView):
    """
    Страница профиля пользователя.
    """
    template_name = 'profile.html'


class RoomsView(TemplateView):
    """
    Страница списка комнат.
    """
    template_name = 'rooms.html'


class RoomDetailView(TemplateView):
    """
    Страница детальной информации о комнате.
    """
    template_name = 'room_detail.html'


class BookingsView(TemplateView):
    """
    Страница списка бронирований пользователя.
    """
    template_name = 'bookings.html'
