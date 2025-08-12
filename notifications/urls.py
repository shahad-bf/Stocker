from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<uuid:pk>/mark-read/', views.mark_notification_read, name='mark_read'),
    path('<uuid:pk>/send-email/', views.send_notification_email, name='send_email'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
    path('send-all-emails/', views.send_all_notifications_email, name='send_all_emails'),
    path('bulk-send-emails/', views.bulk_send_emails, name='bulk_send_emails'),
    path('generate-stock-notifications/', views.generate_stock_notifications, name='generate_stock_notifications'),
    
    # API endpoints
    path('api/count/', views.notification_count_api, name='api_count'),
    path('api/recent/', views.recent_notifications_api, name='api_recent'),
]
