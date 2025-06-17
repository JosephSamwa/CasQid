from django.urls import path
from .views import (
    PaymentDetailView,
    PaymentHistoryView,
    PaymentAnalyticsView,
    JobPaymentHistoryView,
    payment_list,
    initiate_mpesa_payment,
    PaymentProcessView,
    PaymentConfirmationView
)
from . import views

urlpatterns = [
    path('initiate/<int:job_id>/', views.initiate_payment, name='initiate_payment'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
    path('history/', views.payment_history, name='payment_history'),
    path('guide/<int:job_id>/', views.guide, name='guide'),
    path('add-mpesa-transaction/', views.add_mpesa_transaction, name='add_mpesa_transaction'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payment_analytics/', PaymentAnalyticsView.as_view(), name='payment_analytics'),
    path('job/<int:job_id>/payments/', JobPaymentHistoryView.as_view(), name='job_payment_history'),
    path('payments/', payment_list, name='payment_list'),
    path('initiate_payment/', initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('process_payment/', PaymentProcessView.as_view(), name='process_payment'),
    path('confirm_payment/<int:pk>/', PaymentConfirmationView.as_view(), name='payment_confirmation'),
]
