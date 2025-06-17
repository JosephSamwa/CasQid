from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm
from feedback.views import get_testimonials
from .utils import send_contact_message_email  # Import the email function

class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact/contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()

            try:
                # Send email notification to admin
                send_contact_message_email(contact_message)

                messages.success(request, 
                    """<div class='d-flex align-items-center'>
                        <i class='fas fa-check-circle me-2'></i>
                        <div>
                            <strong>Message sent!</strong><br>
                            <span class='small'>We'll get back to you soon.</span>
                        </div>
                    </div>"""
                )
            except Exception as e:
                messages.error(request, 
                    f"""<div class='d-flex align-items-center'>
                        <i class='fas fa-exclamation-circle me-2'></i>
                        <div>
                            <strong>Error sending message</strong><br>
                            <span class='small'>Please try again later.</span>
                        </div>
                    </div>"""
                )
                contact_message.delete()  # Delete the message if email fails

            return redirect('contact')
        
        messages.error(request, 
            """<div class='d-flex align-items-center'>
                <i class='fas fa-exclamation-circle me-2'></i>
                <div>
                    <strong>Form validation error</strong><br>
                    <span class='small'>Please check your inputs.</span>
                </div>
            </div>"""
        )
        return render(request, 'contact/contact.html', {'form': form})


class FAQView(View):
    def get(self, request):
        return render(request, 'contact/faq.html')

def about(request):
    context = {
        'testimonials': get_testimonials(request)
    }
    return render(request, 'about.html', context)