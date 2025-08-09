from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, F
from .models import Product, Category


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = [
        'name', 'sku', 'barcode', 'description', 'category',
        'unit_price', 'cost_price', 'selling_price', 'unit',
        'stock_quantity', 'minimum_stock', 'maximum_stock', 'reorder_level',
        'weight', 'dimensions', 'color', 'size', 'material', 'brand', 'model_number',
        'has_expiry', 'expiry_date', 'shelf_life_days', 'image', 'is_active', 'is_featured'
    ]
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = [
        'name', 'sku', 'barcode', 'description', 'category',
        'unit_price', 'cost_price', 'selling_price', 'unit',
        'stock_quantity', 'minimum_stock', 'maximum_stock', 'reorder_level',
        'weight', 'dimensions', 'color', 'size', 'material', 'brand', 'model_number',
        'has_expiry', 'expiry_date', 'shelf_life_days', 'image', 'is_active', 'is_featured'
    ]
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'products/category_form.html'
    fields = ['name', 'description', 'image', 'is_active']
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'products/category_form.html'
    fields = ['name', 'description', 'image', 'is_active']
    success_url = reverse_lazy('products:category_list')


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category_list')


# API Views
@login_required
def product_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query) | Q(barcode__icontains=query),
        is_active=True
    )[:10]
    
    data = {
        'products': [
            {
                'id': str(product.id),
                'name': product.name,
                'sku': product.sku,
                'stock_quantity': product.stock_quantity,
                'unit_price': str(product.unit_price),
            }
            for product in products
        ]
    }
    
    return JsonResponse(data)


@login_required
def low_stock_api(request):
    products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F('minimum_stock')
    ).select_related('category')[:10]
    
    data = {
        'products': [
            {
                'id': str(product.id),
                'name': product.name,
                'sku': product.sku,
                'stock_quantity': product.stock_quantity,
                'minimum_stock': product.minimum_stock,
                'category': product.category.name,
            }
            for product in products
        ]
    }
    
    return JsonResponse(data)