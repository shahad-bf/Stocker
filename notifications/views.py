from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        ).order_by('-created_at')


class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark as read when viewed
        if not obj.is_read:
            obj.mark_as_read(self.request.user)
        return obj


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.mark_as_read(request.user)
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:notification_list')


@login_required
def mark_all_notifications_read(request):
    count = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True),
        is_read=False
    ).update(is_read=True)
    
    messages.success(request, f'{count} notifications marked as read.')
    return redirect('notifications:notification_list')


# API Views
@login_required
def notification_count_api(request):
    count = Notification.get_unread_count(request.user)
    urgent_count = Notification.get_urgent_count(request.user)
    
    return JsonResponse({
        'total_unread': count,
        'urgent_unread': urgent_count,
    })


@login_required
def recent_notifications_api(request):
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')[:10]
    
    data = {
        'notifications': [
            {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'age_hours': notification.age_in_hours,
            }
            for notification in notifications
        ]
    }
    
    return JsonResponse(data)