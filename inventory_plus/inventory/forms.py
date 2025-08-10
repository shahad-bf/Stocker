from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Submit, Div, HTML
from crispy_forms.bootstrap import InlineRadios
from .models import Product, Category, Supplier, StockMovement, UserProfile


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', placeholder='Username', css_class='form-control-lg'),
            Field('password', placeholder='Password', css_class='form-control-lg'),
            Div(
                Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100'),
                css_class='d-grid gap-2'
            )
        )


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('role', css_class='form-group col-md-4 mb-0'),
                Column('phone_number', css_class='form-group col-md-4 mb-0'),
                Column('department', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Create User', css_class='btn btn-success'),
                css_class='text-center'
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update user profile
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.phone_number = self.cleaned_data['phone_number']
            profile.department = self.cleaned_data['department']
            profile.save()
        
        return user


class CategoryForm(forms.ModelForm):
    """Form for Category model"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Field('name', placeholder='Category Name'),
            Field('description', placeholder='Category Description'),
            Field('image'),
            Field('is_active'),
            Div(
                Submit('submit', 'Save Category', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class SupplierForm(forms.ModelForm):
    """Form for Supplier model"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'logo', 'email', 'website', 'phone_number', 'address',
            'contact_person', 'tax_number', 'payment_terms', 'rating', 'notes', 'is_active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 0.1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h4>Basic Information</h4>'),
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('website', css_class='form-group col-md-6 mb-0'),
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('logo'),
            Field('address'),
            HTML('<hr><h4>Contact Details</h4>'),
            Row(
                Column('contact_person', css_class='form-group col-md-6 mb-0'),
                Column('tax_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('payment_terms', css_class='form-group col-md-6 mb-0'),
                Column('rating', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('notes'),
            Field('is_active'),
            Div(
                Submit('submit', 'Save Supplier', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class ProductForm(forms.ModelForm):
    """Form for Product model"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'barcode', 'description', 'category', 'suppliers',
            'unit_price', 'cost_price', 'selling_price', 'unit',
            'stock_quantity', 'minimum_stock', 'maximum_stock', 'reorder_level',
            'weight', 'dimensions', 'color', 'size', 'material', 'brand', 'model_number',
            'has_expiry', 'expiry_date', 'shelf_life_days',
            'image', 'is_active', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'suppliers': forms.CheckboxSelectMultiple(),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'unit_price': forms.NumberInput(attrs={'step': 0.01}),
            'cost_price': forms.NumberInput(attrs={'step': 0.01}),
            'selling_price': forms.NumberInput(attrs={'step': 0.01}),
            'weight': forms.NumberInput(attrs={'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h4>Basic Information</h4>'),
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column('sku', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('barcode', css_class='form-group col-md-6 mb-0'),
                Column('category', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('description'),
            Field('suppliers'),
            
            HTML('<hr><h4>Pricing</h4>'),
            Row(
                Column('unit_price', css_class='form-group col-md-3 mb-0'),
                Column('cost_price', css_class='form-group col-md-3 mb-0'),
                Column('selling_price', css_class='form-group col-md-3 mb-0'),
                Column('unit', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<hr><h4>Stock Management</h4>'),
            Row(
                Column('stock_quantity', css_class='form-group col-md-3 mb-0'),
                Column('minimum_stock', css_class='form-group col-md-3 mb-0'),
                Column('maximum_stock', css_class='form-group col-md-3 mb-0'),
                Column('reorder_level', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<hr><h4>Product Details</h4>'),
            Row(
                Column('weight', css_class='form-group col-md-4 mb-0'),
                Column('dimensions', css_class='form-group col-md-4 mb-0'),
                Column('color', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('size', css_class='form-group col-md-4 mb-0'),
                Column('material', css_class='form-group col-md-4 mb-0'),
                Column('brand', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Field('model_number'),
            
            HTML('<hr><h4>Expiry Management</h4>'),
            Field('has_expiry'),
            Row(
                Column('expiry_date', css_class='form-group col-md-6 mb-0'),
                Column('shelf_life_days', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<hr><h4>Media & Status</h4>'),
            Field('image'),
            Row(
                Column('is_active', css_class='form-group col-md-6 mb-0'),
                Column('is_featured', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Div(
                Submit('submit', 'Save Product', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        has_expiry = cleaned_data.get('has_expiry')
        expiry_date = cleaned_data.get('expiry_date')
        shelf_life_days = cleaned_data.get('shelf_life_days')

        if has_expiry and not expiry_date and not shelf_life_days:
            raise ValidationError("Please provide either expiry date or shelf life days for perishable items.")

        return cleaned_data


class StockMovementForm(forms.ModelForm):
    """Form for Stock Movement"""
    
    class Meta:
        model = StockMovement
        fields = [
            'product', 'movement_type', 'quantity', 'unit_cost', 
            'reference_number', 'notes', 'supplier'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'unit_cost': forms.NumberInput(attrs={'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='form-group col-md-6 mb-0'),
                Column('movement_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                Column('unit_cost', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('reference_number', css_class='form-group col-md-6 mb-0'),
                Column('supplier', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('notes'),
            Div(
                Submit('submit', 'Record Movement', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class StockUpdateForm(forms.Form):
    """Quick form for updating stock quantities"""
    quantity = forms.IntegerField(min_value=0, help_text="Enter new stock quantity")
    movement_type = forms.ChoiceField(
        choices=[
            ('in', 'Stock In'),
            ('out', 'Stock Out'),
            ('adjustment', 'Stock Adjustment'),
        ]
    )
    reference_number = forms.CharField(max_length=100, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                Column('movement_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('reference_number'),
            Field('notes'),
            Div(
                Submit('submit', 'Update Stock', css_class='btn btn-warning'),
                css_class='text-center'
            )
        )


class SearchForm(forms.Form):
    """Search form for products"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search products, SKU, or barcode...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True),
        required=False,
        empty_label="All Suppliers"
    )
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All Stock Levels'),
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-3 mb-0'),
                Column('supplier', css_class='form-group col-md-3 mb-0'),
                Column('stock_status', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Search', css_class='btn btn-outline-primary'),
                css_class='text-center mt-3'
            )
        )



