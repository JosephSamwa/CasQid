from django.shortcuts import render, redirect,  get_object_or_404, redirect
from django.http import HttpResponse
from .models import Payment
from django.conf import settings
import requests
import json
from django.views import View
from .forms import PaymentForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from jobs.models import Job
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from jobs.models import Job
from applications.models import Application
from django.contrib import messages
import logging
from users.models import UserProfile
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .utils import extract_mpesa_details
from django.http import JsonResponse
from django.db import transaction
import re
from applications.utils import send_application_email
logger = logging.getLogger(__name__)

class MPesaMessageParser:
    def extract_transaction_id(self, message):
        # Assuming transaction ID is the first word in the message
        parts = message.split()
        if parts and len(parts[0]) == 10:  # M-Pesa transaction IDs are typically 10 characters
            return parts[0]
        return None

    def extract_amount(self, message):
        # Look for "KES X.XX" pattern
        if "KES" in message:
            parts = message.split("KES")
            if len(parts) > 1:
                amount_part = parts[1].strip().split()[0]
                try:
                    return float(amount_part.replace(',', ''))
                except ValueError:
                    return None
        return None

    def extract_phone(self, message):
        # Look for "tel XXXXXXXXX" pattern
        if "tel" in message:
            parts = message.split("tel")
            if len(parts) > 1:
                return parts[1].strip().split()[0]
        return None

    def extract_date(self, message):
        # Look for date and time information
        if "on" in message and "at" in message:
            date_parts = message.split("on")
            if len(date_parts) > 1:
                datetime_part = date_parts[1].strip()
                return datetime_part.split("Enquiries")[0].strip()
        return None

@csrf_exempt
@require_POST
def add_mpesa_transaction(request):
    try:
        # Log incoming request
        logger.info("Received M-Pesa transaction request")
        print("Received M-Pesa transaction request")
        try:
            post_data = json.loads(request.body)
            logger.debug("Received M-Pesa transaction request data: %s", post_data)
            print("Received M-Pesa transaction request data: %s", post_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {str(e)}")
            print(f"Invalid JSON data: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Extract message
        mpesa_message = post_data.get('key')
        if not mpesa_message:
            logger.error("No M-Pesa message provided")
            print("No M-Pesa message provided")
            return JsonResponse({'error': 'M-Pesa message is required'}, status=400)

        # Parse message using the updated parser
        parser = MPesaMessageParser()
        transaction_id = parser.extract_transaction_id(mpesa_message)
        amount = parser.extract_amount(mpesa_message)
        phone_number = parser.extract_phone(mpesa_message)
        transaction_date = parser.extract_date(mpesa_message)

        # Validate extracted data
        if not all([transaction_id, amount, phone_number, transaction_date]):
            logger.error("Failed to extract all required fields", extra={
                'transaction_id': transaction_id,
                'amount': amount,
                'phone': phone_number,
                'date': transaction_date
            })
            print("Failed to extract all required fields")
            return JsonResponse({
                'error': 'Invalid M-Pesa message format',
                'missing_fields': [
                    field for field, value in {
                        'transaction_id': transaction_id,
                        'amount': amount,
                        'phone_number': phone_number,
                        'transaction_date': transaction_date
                    }.items() if not value
                ]
            }, status=400)

        # Use transaction atomic to ensure database consistency
        with transaction.atomic():
            print("Database consistency")
            transaction_obj, created = Payment.objects.get_or_create(
                transaction_id=transaction_id,
                defaults={
                    'amount': amount,
                    'phone_number': phone_number,
                    'transaction_date': transaction_date
                }
            )

        # Log success
        logger.info(
            "Transaction processed successfully",
            extra={
                'transaction_id': transaction_id,
                'created': created
            }
        )
        print("Transaction processed successfully")
        if created:
            return JsonResponse({
                    'message': 'Transaction processed successfully',
                    'status': 'created',
                    'transaction_id': transaction_id
                }, status=201)
        else:
            return JsonResponse({
                'message': 'Transaction already exists', 
                'status': 'existing'}, status=200)

    except Exception as e:
        logger.exception("Unexpected error processing M-Pesa transaction")
        print("Unexpected error processing M-Pesa transaction")
        return JsonResponse({'error': 'Invalid M-Pesa message'}, status=400)


@login_required
@csrf_exempt
def guide(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    formatted_commission_fee = f"{job.commission_fee:,.2f}"
    if request.method == 'POST':
        return redirect('initiate_payment', job.id)

    # Your implementation here
    return render(request, 'payments/guide.html', {'job': job, 'formatted_commission_fee': formatted_commission_fee})

@login_required
@csrf_exempt
def initiate_payment(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        mpesa_message = request.POST.get('mpesa_message', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        fee = job.commission_fee

        if not mpesa_message:
            messages.error(request, "M-Pesa message is required.")
            return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

        try:
            # Extract transaction details
            transaction_details = extract_mpesa_details(mpesa_message)
            transaction_id = transaction_details.get('transaction_id')
            amount = transaction_details.get('amount')
            transaction_date = transaction_details.get('transaction_date')
            sender_phone = transaction_details.get('phone_number')

            # Check if transaction already exists
            transact = Payment.objects.filter(transaction_id=transaction_id)
            if transact.exists():
                transaction = transact.first()
            else:
                messages.error(request, "The transaction doesn't exist!.Please try again or contact support.")
                return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))
            # Validate extracted details
            if not all([transaction_id, amount, transaction_date]):
                messages.error(request, "Invalid M-Pesa message. Please check and try again.")
                return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

            # Use sender phone if available
            phone_number = sender_phone or phone_number

            # Ensure the amount matches
            if round(float(amount), 2) != round(float(fee), 2):
                messages.error(request, f"Amount mismatch. You paid {amount} but the required fee is {fee}.")
                return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

            # Now we're dealing with a single transaction object, not a queryset
            if transaction.is_used:
                messages.error(request, "This transaction has already been used.")
                return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

            if transaction.phone_number and transaction.phone_number != phone_number:
                messages.error(request, "Transaction details do not match the provided phone number.")
                return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

            # Mark transaction as completed
            transaction.transaction_date = transaction_date
            transaction.status = 'completed'
            transaction.user = request.user
            transaction.job = job
            transaction.is_used = True
            transaction.save()

            application = Application.objects.filter(
                    user=request.user, 
                    job=job
                ).first()
            application.payment = transaction
            application.save()
            send_application_email(application)
            messages.success(request, "Payment successful!")
            return redirect(reverse('payment_success', kwargs={'payment_id': transaction.id}))

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            messages.error(request, f"Unexpected error: {str(e)} occurred. Please try again later or contact support.")
            return redirect(reverse('initiate_payment', kwargs={'job_id': job.id}))

    return render(request, 'payments/initiate_payment.html', {'job': job})


def extract_mpesa_details(mpesa_message):
    """
    Extracts transaction details from an M-Pesa message.
    
    Expected format (example):
    "PGB56HTY Confirmed. Ksh1,000.00 sent to JOHN DOE on 3/12/25 at 2:15 PM. New M-PESA balance is Ksh2,500.00."
    
    Returns a dictionary with:
    - transaction_id
    - amount (as float)
    - transaction_date (as datetime)
    - phone_number (if available)
    """
    import re
    from datetime import datetime
    
    details = {}
    
    # Extract transaction ID (usually at the beginning)
    transaction_id_match = re.search(r'^([A-Z0-9]+)\s+Confirmed', mpesa_message)
    if transaction_id_match:
        details['transaction_id'] = transaction_id_match.group(1)
    
    # Extract amount
    amount_match = re.search(r'Ksh([\d,]+\.\d{2})', mpesa_message)
    if amount_match:
        amount_str = amount_match.group(1).replace(',', '')
        details['amount'] = float(amount_str)
    
    # Extract date and time
    date_match = re.search(r'on\s+(\d{1,2}/\d{1,2}/\d{2})\s+at\s+(\d{1,2}:\d{2}\s+[AP]M)', mpesa_message)
    if date_match:
        date_str = date_match.group(1)
        time_str = date_match.group(2)
        datetime_str = f"{date_str} {time_str}"
        try:
            transaction_date = datetime.strptime(datetime_str, "%m/%d/%y %I:%M %p")
            details['transaction_date'] = transaction_date
        except ValueError:
            # If date format doesn't match, use current time
            details['transaction_date'] = datetime.now()
    
    # Try to extract phone number if present
    phone_match = re.search(r'from\s+(\d{10,12})', mpesa_message)
    if phone_match:
        details['phone_number'] = phone_match.group(1)
    
    return details



@login_required
def payment_success(request, payment_id):
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        logger.info(f"Payment success view accessed for payment_id: {payment_id}")
        return render(request, 'payments/payment_success.html', {'payment_id': payment_id, 'payment': payment})
    except Payment.DoesNotExist:
        logger.error(f"Payment with id {payment_id} not found")
        messages.error(request, "Payment not found.")
        return redirect('payment_failure')

@login_required
def payment_failure(request):
    return render(request, 'payments/payment_failure.html', {'error': 'Payment failed. Please try again.'})

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/payment_history.html', {'payments': payments})

class UserDashboardView(LoginRequiredMixin, View):
    template_name = 'user_dashboard.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        user = request.user
        context = self.get_context_data(user)
        return render(request, self.template_name, context)

    def get_context_data(self, user):
        # Get all payments for the user
        payments = Payment.objects.filter(user=user).order_by('-transaction_date')

        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(payments, self.paginate_by)
        try:
            payments = paginator.page(page)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        # Calculate total amount paid
        total_paid = Payment.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        # Get payment statistics
        payment_stats = self.get_payment_stats(user)

        # Get recent jobs (fixed to use transaction_date instead of created_at)
        recent_jobs = Job.objects.filter(payment__user=user).distinct().order_by('-payment__transaction_date')[:5]

        # Get payment method distribution
        payment_methods = Payment.objects.filter(user=user).values('payment_method').annotate(count=Count('payment_method'))

        context = {
            'user': user,
            'payments': payments,
            'total_paid': total_paid,
            'payment_stats': payment_stats,
            'recent_jobs': recent_jobs,
            'payment_methods': payment_methods,
        }
        return context

    def get_payment_stats(self, user):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        total_payments = Payment.objects.filter(user=user).count()
        # Update to use lowercase status values that match the choices in the model
        completed_payments = Payment.objects.filter(user=user, status='completed').count()
        pending_payments = Payment.objects.filter(user=user, status='pending').count()
        failed_payments = Payment.objects.filter(user=user, status='failed').count()
        # Fixed to use transaction_date instead of created_at
        recent_payments = Payment.objects.filter(user=user, transaction_date__gte=thirty_days_ago).count()

        return {
            'total': total_payments,
            'completed': completed_payments,
            'pending': pending_payments,
            'failed': failed_payments,
            'recent': recent_payments,
        }

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payment_detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-transaction_date')

class PaymentAnalyticsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        payments = Payment.objects.filter(user=user)

        # Calculate monthly payment totals
        monthly_totals = payments.extra(select={'month': "DATE_TRUNC('month', transaction_date)"}) \
                                 .values('month') \
                                 .annotate(total=Sum('amount')) \
                                 .order_by('month')

        # Calculate payment method distribution
        payment_methods = payments.values('payment_method') \
                                  .annotate(count=Count('payment_method')) \
                                  .order_by('-count')

        # Calculate success rate
        total_payments = payments.count()
        successful_payments = payments.filter(status='Completed').count()
        success_rate = (successful_payments / total_payments) * 100 if total_payments > 0 else 0

        data = {
            'monthly_totals': list(monthly_totals),
            'payment_methods': list(payment_methods),
            'success_rate': success_rate,
        }

        return JsonResponse(data)

class JobPaymentHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'job_payment_history.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return Payment.objects.filter(user=self.request.user, job_id=job_id).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        context['job'] = Job.objects.get(id=job_id)
        return context
def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'payments/payment_list.html', {'payments': payments})


def initiate_mpesa_payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        phone_number = request.POST.get("phone_number")

        # Mpesa API credentials
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        access_token = get_mpesa_access_token(consumer_key, consumer_secret)

        # Mpesa endpoint and request payload
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
            "Password": settings.MPESA_PASSWORD,
            "Timestamp": settings.MPESA_TIMESTAMP,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "TravelBooking",
            "TransactionDesc": "Travel booking payment"
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response_data.get("ResponseCode") == "0":
            Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_method="Mpesa",
                mpesa_transaction_id=response_data.get("CheckoutRequestID")
            )
            return redirect("payment_list")
        else:
            return HttpResponse("Payment failed", status=400)
    
    return render(request, 'payments/initiate_payment.html')

def get_mpesa_access_token(consumer_key, consumer_secret):
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    response_data = response.json()
    return response_data.get("access_token")




class PaymentProcessView(View):
    def get(self, request):
        form = PaymentForm()
        return render(request, 'payments/payment_process.html', {'form': form})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()
            # Process payment with payment gateway
            return redirect('payment_confirmation', pk=payment.pk)
        return render(request, 'payments/payment_process.html', {'form': form})

class PaymentConfirmationView(View):
    def get(self, request, pk):
        payment = Payment.objects.get(pk=pk)
        return render(request, 'payments/payment_confirmation.html', {'payment': payment})

