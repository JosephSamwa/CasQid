from django.urls import path
from . import views


urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('track/', views.appointment_tracking, name='appointment_tracking'),
    
    # Admin URLs
    path('admin/appointments/', views.appointment_list, name='admin_appointment_list'),
    path('admin/appointments/<int:pk>/approve/', views.approve_appointment, name='approve_appointment'),
    path('admin/appointments/<int:pk>/reject/', views.reject_appointment, name='reject_appointment'),
    path('admin/appointments/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
    path('admin/appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
]