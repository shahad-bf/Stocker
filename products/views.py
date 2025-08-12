from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Category
from .forms import CategoryForm, ProductForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Search by name or SKU
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(sku__icontains=query)
            )
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by stock status
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'high':
            queryset = queryset.filter(stock_quantity__gt=F('minimum_stock'))
        elif stock_status == 'low':
            queryset = queryset.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=F('minimum_stock')
            )
        elif stock_status == 'out':
            queryset = queryset.filter(stock_quantity=0)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def delete(self, request, *args, **kwargs):
        """
        Simple deletion - just deactivate the product
        """
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        
        self.object = self.get_object()
        product_name = self.object.name
        
        # Simply deactivate the product
        self.object.is_active = False
        self.object.save()
        
        messages.success(
            request, 
            f'Product "{product_name}" has been deactivated successfully.'
        )
        
        return HttpResponseRedirect(self.success_url)


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
    form_class = CategoryForm
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'products/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        return super().form_valid(form)


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


@login_required
@require_POST
def delete_product_ajax(request, pk):
    """Delete product via AJAX"""
    try:
        product = get_object_or_404(Product, pk=pk)
        product_name = product.name
        
        # Check if product can be safely deleted
        if not product.can_be_deleted():
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete "{product_name}" because it has stock movements. Product has been deactivated instead.'
            })
        
        # Deactivate instead of hard delete
        product.is_active = False
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Product "{product_name}" has been deleted successfully.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting product: {str(e)}'
        })

