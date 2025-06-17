# notifications/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('create/', views.NotificationCreateView.as_view(), name='notification_create'),
    path('<int:pk>/update/', views.NotificationUpdateView.as_view(), name='notification_update'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    path('<int:pk>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
]
