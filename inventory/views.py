from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Sum, F
from django.contrib import messages
from .models import StockMovement, InventoryTransaction, StockAlert


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20
    
    def get_queryset(self):
        return StockMovement.objects.select_related('product', 'created_by', 'supplier')


class StockMovementDetailView(LoginRequiredMixin, DetailView):
    model = StockMovement
    template_name = 'inventory/movement_detail.html'
    context_object_name = 'movement'


class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    template_name = 'inventory/movement_form.html'
    fields = [
        'product', 'movement_type', 'quantity', 'unit_cost', 
        'reference_number', 'notes', 'supplier'
    ]
    success_url = reverse_lazy('inventory:movement_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Set previous stock and calculate new stock
        product = form.instance.product
        form.instance.previous_stock = product.stock_quantity
        
        if form.instance.movement_type == 'in':
            form.instance.new_stock = product.stock_quantity + form.instance.quantity
        elif form.instance.movement_type == 'out':
            form.instance.new_stock = product.stock_quantity - form.instance.quantity
        else:  # adjustment
            form.instance.new_stock = form.instance.quantity
        
        return super().form_valid(form)


class InventoryTransactionListView(LoginRequiredMixin, ListView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20


class InventoryTransactionDetailView(LoginRequiredMixin, DetailView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_detail.html'
    context_object_name = 'transaction'


class InventoryTransactionCreateView(LoginRequiredMixin, CreateView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_form.html'
    fields = [
        'transaction_type', 'reference_number', 'description', 
        'supplier', 'total_amount', 'tax_amount'
    ]
    success_url = reverse_lazy('inventory:transaction_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class StockAlertListView(LoginRequiredMixin, ListView):
    model = StockAlert
    template_name = 'inventory/alert_list.html'
    context_object_name = 'alerts'


class StockAlertCreateView(LoginRequiredMixin, CreateView):
    model = StockAlert
    template_name = 'inventory/alert_form.html'
    fields = [
        'product', 'alert_type', 'threshold_value', 'is_active',
        'email_notifications', 'notify_users', 'notify_roles'
    ]
    success_url = reverse_lazy('inventory:alert_list')


class StockAlertUpdateView(LoginRequiredMixin, UpdateView):
    model = StockAlert
    template_name = 'inventory/alert_form.html'
    fields = [
        'product', 'alert_type', 'threshold_value', 'is_active',
        'email_notifications', 'notify_users', 'notify_roles'
    ]
    success_url = reverse_lazy('inventory:alert_list')


class StockAlertDeleteView(LoginRequiredMixin, DeleteView):
    model = StockAlert
    template_name = 'inventory/alert_confirm_delete.html'
    success_url = reverse_lazy('inventory:alert_list')


# Function-based views
@login_required
def stock_adjustment_view(request, product_id):
    from products.models import Product
    from django.db import transaction
    
    try:
        product = get_object_or_404(Product, id=product_id)
    except Exception as e:
        messages.error(request, f'المنتج غير موجود: {e}')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 0))
            movement_type = request.POST.get('movement_type', 'adjustment')
            notes = request.POST.get('notes', '').strip()
            
            if quantity <= 0:
                messages.error(request, 'الكمية يجب أن تكون أكبر من 0')
                return render(request, 'inventory/stock_adjust.html', {'product': product})
            
            # Calculate new stock based on movement type
            current_stock = product.stock_quantity
            
            if movement_type == 'in':
                new_stock = current_stock + quantity
            elif movement_type == 'out':
                new_stock = max(0, current_stock - quantity)  # Don't allow negative stock
            else:  # adjustment
                new_stock = quantity
            
            # Use database transaction to ensure consistency
            with transaction.atomic():
                # Create stock movement record
                stock_movement = StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    previous_stock=current_stock,
                    new_stock=new_stock,
                    notes=notes or None,
                    created_by=request.user
                    # Don't include supplier field at all
                )
                
                # Update product stock
                product.stock_quantity = new_stock
                product.save()
            
            # Add success message
            movement_display = {
                'in': 'إدخال مخزون',
                'out': 'إخراج مخزون', 
                'adjustment': 'تعديل مخزون'
            }
            messages.success(request, f'تم {movement_display.get(movement_type, "تحديث")} {product.name} بنجاح. المخزون الجديد: {new_stock} {product.unit}')
            
            # Redirect back to products list
            return redirect('products:product_list')
            
        except ValueError as e:
            messages.error(request, 'خطأ في البيانات المدخلة. تأكد من صحة الأرقام.')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث المخزون: {str(e)}')
    
    return render(request, 'inventory/stock_adjust.html', {'product': product})


@login_required
def bulk_stock_adjustment_view(request):
    # Implementation for bulk stock adjustment
    return render(request, 'inventory/bulk_adjust.html')


@login_required
def complete_transaction(request, pk):
    transaction = get_object_or_404(InventoryTransaction, pk=pk)
    transaction.complete_transaction(request.user)
    messages.success(request, f'Transaction {transaction.reference_number} completed.')
    return redirect('inventory:transaction_detail', pk=pk)


@login_required
def cancel_transaction(request, pk):
    transaction = get_object_or_404(InventoryTransaction, pk=pk)
    transaction.cancel_transaction()
    messages.success(request, f'Transaction {transaction.reference_number} cancelled.')
    return redirect('inventory:transaction_detail', pk=pk)


# Report views
@login_required
def stock_report_view(request):
    from products.models import Product
    products = Product.objects.filter(is_active=True).select_related('category')
    return render(request, 'inventory/stock_report.html', {'products': products})


@login_required
def movement_report_view(request):
    movements = StockMovement.objects.select_related('product', 'created_by')
    return render(request, 'inventory/movement_report.html', {'movements': movements})


@login_required
def valuation_report_view(request):
    from products.models import Product
    products = Product.objects.filter(is_active=True).annotate(
        total_value=F('stock_quantity') * F('unit_price')
    )
    total_valuation = products.aggregate(total=Sum('total_value'))['total'] or 0
    
    return render(request, 'inventory/valuation_report.html', {
        'products': products,
        'total_valuation': total_valuation
    })


# API Views
@login_required
def stock_levels_api(request):
    from products.models import Product
    products = Product.objects.filter(is_active=True).values(
        'id', 'name', 'sku', 'stock_quantity', 'minimum_stock'
    )
    
    return JsonResponse({'products': list(products)})


@login_required
def recent_movements_api(request):
    movements = StockMovement.objects.select_related('product').order_by('-created_at')[:10]
    
    data = {
        'movements': [
            {
                'id': str(movement.id),
                'product_name': movement.product.name,
                'movement_type': movement.get_movement_type_display(),
                'quantity': movement.quantity,
                'created_at': movement.created_at.isoformat(),
            }
            for movement in movements
        ]
    }
    
    return JsonResponse(data)