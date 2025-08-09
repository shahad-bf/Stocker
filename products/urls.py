from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product URLs
    path('', views.ProductListView.as_view(), name='product_list'),
    path('add/', views.ProductCreateView.as_view(), name='product_add'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<uuid:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('<uuid:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<uuid:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<uuid:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # API endpoints
    path('api/search/', views.product_search_api, name='api_product_search'),
    path('api/low-stock/', views.low_stock_api, name='api_low_stock'),
]
