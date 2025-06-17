from django.urls import path
from . import views

urlpatterns = [
    path('apply/<int:job_id>/', views.submit_application, name='apply'),
    path('requirements/<int:job_id>/', views.requirements, name='requirements'),
    path('application-list/', views.application_list, name='application_list'),
    path('admin/application-list/', views.admin_application_list, name='admin_application_list'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('application-detail/<int:application_id>/', views.application_detail, name='application_detail'),
]
