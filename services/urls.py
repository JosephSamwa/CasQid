from django.urls import path
from .views import add_service, service_list, service_detail

urlpatterns = [
    path('services/add/', add_service, name='add_service'),
    path('', service_list, name='services'),
    path('service/<int:service_id>/', service_detail, name='service_detail'),
]
