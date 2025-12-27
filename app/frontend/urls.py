from django.urls import path
from .views import IndexView, RegisterView, LoginView, ProfileView, RoomsView, RoomDetailView, BookingsView

app_name = 'frontend'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('rooms/', RoomsView.as_view(), name='rooms'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('bookings/', BookingsView.as_view(), name='bookings'),
]
