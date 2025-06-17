from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback
from .forms import FeedbackForm
from django.conf import settings
from .utils import send_feedback_email

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()

            # Send email notification to admin
            send_feedback_email(feedback)

            messages.success(request, 
                """<div class='d-flex align-items-center'>
                    <i class='fas fa-check-circle me-2'></i>
                    <div>
                        <strong>Thank you for your feedback!</strong><br>
                        <span class='small'>We appreciate you taking the time to share your experience.</span>
                    </div>
                </div>"""
            )
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            messages.error(request, "Please check your input and try again.")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))



def get_testimonials(request):
    """Get approved testimonials for template context"""
    return Feedback.objects.filter(
        consent_to_testimonial=True,
        approved=True
    ).select_related('user')[:6]
