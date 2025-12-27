from django.urls import path
from .views import (
    RoomListView,
    RoomDetailView,
    RoomAvailabilityView,
)

urlpatterns = [
    path('', RoomListView.as_view(), name='room-list'),
    path('available/', RoomAvailabilityView.as_view(), name='room-availability'),
    path('<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
]
