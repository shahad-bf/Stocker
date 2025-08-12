from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import Field
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name', 'logo', 'email', 'website', 'phone_number', 'address',
            'contact_person', 'tax_number', 'payment_terms', 'rating', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full Address'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Person Name'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tax Number'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment Terms (e.g., 30 days)'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '5',
                'step': '0.1',
                'placeholder': 'Rating from 0 to 5'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional Notes'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': '', 'enctype': 'multipart/form-data'}
        
        # Add required attributes
        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({'required': 'required'})
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'required': 'required'})
        
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="text-primary mb-3"><i class="bi bi-info-circle me-2"></i>Basic Information</h6>'),
                Row(
                    Column(
                        Field('name', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('email', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(
                        Field('website', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('phone_number', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(
                        Field('address', css_class='mb-3'),
                        css_class='col-12'
                    ),
                ),
                
                HTML('<hr><h6 class="text-success mb-3"><i class="bi bi-person me-2"></i>Contact Information</h6>'),
                Row(
                    Column(
                        Field('contact_person', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('tax_number', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(
                        Field('payment_terms', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('rating', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                ),
                
                HTML('<hr><h6 class="text-info mb-3"><i class="bi bi-image me-2"></i>Logo & Notes</h6>'),
                Row(
                    Column(
                        Field('logo', css_class='mb-3'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('is_active', css_class='mb-3 form-check form-switch'),
                        css_class='col-md-6'
                    ),
                ),
                Row(
                    Column(
                        Field('notes', css_class='mb-3'),
                        css_class='col-12'
                    ),
                ),
                
                HTML('<hr>'),
                Row(
                    Column(
                        Submit('submit', 'Save Supplier', css_class='btn btn-primary btn-lg me-2'),
                        HTML('<a href="{% url \'suppliers:supplier_list\' %}" class="btn btn-secondary btn-lg">Cancel</a>'),
                        css_class='col-12 text-center'
                    ),
                ),
                css_class='card-body'
            )
        )
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None:
            if rating < 0 or rating > 5:
                raise forms.ValidationError('Rating must be between 0 and 5')
        return rating
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is unique (excluding current instance)
            existing = Supplier.objects.filter(email=email)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError('This email address is already in use')
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if name is unique (excluding current instance)
            existing = Supplier.objects.filter(name=name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError('Supplier name already exists')
        return name
