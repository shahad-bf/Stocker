from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Stock movement URLs
    path('movements/', views.StockMovementListView.as_view(), name='movement_list'),
    path('movements/add/', views.StockMovementCreateView.as_view(), name='movement_add'),
    path('movements/<uuid:pk>/', views.StockMovementDetailView.as_view(), name='movement_detail'),
    
    # Stock adjustment
    path('adjust/<uuid:product_id>/', views.stock_adjustment_view, name='stock_adjust'),
    path('bulk-adjust/', views.bulk_stock_adjustment_view, name='bulk_adjust'),
    
    # Transactions
    path('transactions/', views.InventoryTransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.InventoryTransactionCreateView.as_view(), name='transaction_add'),
    path('transactions/<uuid:pk>/', views.InventoryTransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<uuid:pk>/complete/', views.complete_transaction, name='transaction_complete'),
    path('transactions/<uuid:pk>/cancel/', views.cancel_transaction, name='transaction_cancel'),
    
    # Stock alerts
    path('alerts/', views.StockAlertListView.as_view(), name='alert_list'),
    path('alerts/add/', views.StockAlertCreateView.as_view(), name='alert_add'),
    path('alerts/<uuid:pk>/edit/', views.StockAlertUpdateView.as_view(), name='alert_edit'),
    path('alerts/<uuid:pk>/delete/', views.StockAlertDeleteView.as_view(), name='alert_delete'),
    
    # Reports
    path('reports/stock/', views.stock_report_view, name='stock_report'),
    path('reports/movements/', views.movement_report_view, name='movement_report'),
    path('reports/valuation/', views.valuation_report_view, name='valuation_report'),
    
    # API endpoints
    path('api/stock-levels/', views.stock_levels_api, name='api_stock_levels'),
    path('api/recent-movements/', views.recent_movements_api, name='api_recent_movements'),
]