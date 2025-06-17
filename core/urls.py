from django.urls import path
from . import views
from .utils import test_media_path

urlpatterns = [
    path('', views.home, name='home'),
    path('test-media/', test_media_path, name='test_media_path'),
]