from django.urls import path
from .views import ContactView, FAQView, about

urlpatterns = [
    path('contact/', ContactView.as_view(), name='contact'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('about/', about, name='about'),
]
