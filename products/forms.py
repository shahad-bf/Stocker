from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import Field
from .models import Product, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الفئة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'وصف الفئة (اختياري)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        # Add required attribute to name field
        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({'required': 'required'})
        
        self.helper.layout = Layout(
            Div(
                Row(
                    Column(
                        Field('name', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('is_active', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(
                        Field('description', css_class='mb-3'),
                        css_class='col-12'
                    ),
                ),
                Row(
                    Column(
                        Field('image', css_class='mb-3'),
                        css_class='col-12'
                    ),
                ),
                HTML('<hr>'),
                Row(
                    Column(
                        Submit('submit', 'حفظ التغييرات', css_class='btn btn-primary btn-lg me-2'),
                        HTML('<a href="{% url \'products:category_list\' %}" class="btn btn-secondary btn-lg">إلغاء</a>'),
                        css_class='col-12 text-center'
                    ),
                ),
                css_class='card-body'
            )
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'barcode', 'description', 'category',
            'unit_price', 'cost_price', 'selling_price', 'unit',
            'stock_quantity', 'minimum_stock', 'maximum_stock', 'reorder_level',
            'weight', 'dimensions', 'color', 'size', 'material', 'brand', 'model_number',
            'has_expiry', 'expiry_date', 'shelf_life_days', 'image', 'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المنتج'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رمز المنتج'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الباركود'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'وصف المنتج'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الوحدة (قطعة، كيلو، لتر...)'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'maximum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الأبعاد'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اللون'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الحجم'}),
            'material': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المادة'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العلامة التجارية'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الموديل'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shelf_life_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        # Add required attributes
        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({'required': 'required'})
        self.fields['category'].required = True
        self.fields['category'].widget.attrs.update({'required': 'required'})
        
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="text-primary mb-3"><i class="bi bi-info-circle me-2"></i>معلومات أساسية</h6>'),
                Row(
                    Column(Field('name', css_class='mb-3'), css_class='col-md-6'),
                    Column(Field('sku', css_class='mb-3'), css_class='col-md-6'),
                ),
                Row(
                    Column(Field('barcode', css_class='mb-3'), css_class='col-md-6'),
                    Column(Field('category', css_class='mb-3'), css_class='col-md-6'),
                ),
                Row(
                    Column(Field('description', css_class='mb-3'), css_class='col-12'),
                ),
                
                HTML('<hr><h6 class="text-success mb-3"><i class="bi bi-currency-dollar me-2"></i>معلومات التسعير</h6>'),
                Row(
                    Column(Field('unit_price', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('cost_price', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('selling_price', css_class='mb-3'), css_class='col-md-4'),
                ),
                Row(
                    Column(Field('unit', css_class='mb-3'), css_class='col-md-6'),
                    Column(Field('image', css_class='mb-3'), css_class='col-md-6'),
                ),
                
                HTML('<hr><h6 class="text-warning mb-3"><i class="bi bi-box me-2"></i>إدارة المخزون</h6>'),
                Row(
                    Column(Field('stock_quantity', css_class='mb-3'), css_class='col-md-3'),
                    Column(Field('minimum_stock', css_class='mb-3'), css_class='col-md-3'),
                    Column(Field('maximum_stock', css_class='mb-3'), css_class='col-md-3'),
                    Column(Field('reorder_level', css_class='mb-3'), css_class='col-md-3'),
                ),
                
                HTML('<hr><h6 class="text-info mb-3"><i class="bi bi-tag me-2"></i>مواصفات إضافية</h6>'),
                Row(
                    Column(Field('weight', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('dimensions', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('color', css_class='mb-3'), css_class='col-md-4'),
                ),
                Row(
                    Column(Field('size', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('material', css_class='mb-3'), css_class='col-md-4'),
                    Column(Field('brand', css_class='mb-3'), css_class='col-md-4'),
                ),
                Row(
                    Column(Field('model_number', css_class='mb-3'), css_class='col-md-6'),
                    Column(
                        Row(
                            Column(Field('has_expiry', css_class='mb-3'), css_class='col-6'),
                            Column(Field('expiry_date', css_class='mb-3'), css_class='col-6'),
                        ),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(Field('shelf_life_days', css_class='mb-3'), css_class='col-md-6'),
                    Column(
                        Row(
                            Column(Field('is_active', css_class='mb-3'), css_class='col-6'),
                            Column(Field('is_featured', css_class='mb-3'), css_class='col-6'),
                        ),
                        css_class='col-md-6'
                    ),
                ),
                
                HTML('<hr>'),
                Row(
                    Column(
                        Submit('submit', 'حفظ المنتج', css_class='btn btn-primary btn-lg me-2'),
                        HTML('<a href="{% url \'products:product_list\' %}" class="btn btn-secondary btn-lg">إلغاء</a>'),
                        css_class='col-12 text-center'
                    ),
                ),
                css_class='card-body'
            )
        )
