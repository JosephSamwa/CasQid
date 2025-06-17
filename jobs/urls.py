from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('search/', views.JobSearchView.as_view(), name='job_search'),
]
