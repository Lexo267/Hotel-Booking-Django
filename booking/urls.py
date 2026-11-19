from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('hotels/', views.hotels_view, name='hotels'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('booked/', views.booked_rooms_view, name='booked_rooms'),
]