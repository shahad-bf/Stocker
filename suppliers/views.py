from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Supplier, SupplierProduct
from .forms import SupplierForm


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        return Supplier.objects.filter(is_active=True)


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('suppliers:supplier_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('suppliers:supplier_list')
    
    def form_valid(self, form):
        # Keep track of who last updated the supplier
        return super().form_valid(form)


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')


# API Views
@login_required
def supplier_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suppliers': []})
    
    suppliers = Supplier.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query) | Q(contact_person__icontains=query),
        is_active=True
    )[:10]
    
    data = {
        'suppliers': [
            {
                'id': str(supplier.id),
                'name': supplier.name,
                'email': supplier.email,
                'contact_person': supplier.contact_person,
                'phone_number': supplier.phone_number,
            }
            for supplier in suppliers
        ]
    }
    
    return JsonResponse(data)