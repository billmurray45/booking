from django.urls import path
from .views import (
    BookingCreateView,
    BookingListView,
    BookingDetailView,
    BookingUpdateView,
    BookingCancelView,
)

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/update/', BookingUpdateView.as_view(), name='booking-update'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
]
