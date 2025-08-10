from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.SupplierListView.as_view(), name='supplier_list'),
    path('add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('<uuid:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('<uuid:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('<uuid:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # API endpoints
    path('api/search/', views.supplier_search_api, name='api_supplier_search'),
]
