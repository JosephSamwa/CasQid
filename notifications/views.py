# notifications/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Notification
from .forms import NotificationForm, NotificationFilterForm

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        form = NotificationFilterForm(self.request.GET)
        if form.is_valid():
            notification_type = form.cleaned_data.get('notification_type')
            is_read = form.cleaned_data.get('is_read')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            if notification_type:
                queryset = queryset.filter(notification_type=notification_type)
            if is_read:
                queryset = queryset.filter(is_read=is_read == 'True')
            if date_from:
                queryset = queryset.filter(date_sent__gte=date_from)
            if date_to:
                queryset = queryset.filter(date_sent__lte=date_to)

        return queryset.order_by('-date_sent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = NotificationFilterForm(self.request.GET)
        return context

class NotificationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    template_name = 'notifications/notification_form.html'
    success_url = reverse_lazy('notification_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Notification created successfully.')
        return super().form_valid(form)

class NotificationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Notification
    form_class = NotificationForm
    template_name = 'notifications/notification_form.html'
    success_url = reverse_lazy('notification_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Notification updated successfully.')
        return super().form_valid(form)

class NotificationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Notification
    template_name = 'notifications/notification_confirm_delete.html'
    success_url = reverse_lazy('notification_list')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Notification deleted successfully.')
        return super().delete(request, *args, **kwargs)

def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')

def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')