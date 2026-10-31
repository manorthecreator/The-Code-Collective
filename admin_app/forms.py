from django import forms
from .models import StoreSetting
from products_app.models import Product, ProductVariant

class StoreSettingForm(forms.ModelForm):
    class Meta:
        model = StoreSetting
        fields = [
            'store_name', 'store_email', 'phone', 'currency',
            'timezone', 'legal_name', 'description', 'address',
            'city', 'state'
        ]
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'settings-input'}),
            'store_email': forms.EmailInput(attrs={'class': 'settings-input'}),
            'phone': forms.TextInput(attrs={'class': 'settings-input'}),
            'currency': forms.TextInput(attrs={'class': 'settings-input'}),
            'timezone': forms.TextInput(attrs={'class': 'settings-input'}),
            'legal_name': forms.TextInput(attrs={'class': 'settings-input'}),
            'description': forms.Textarea(attrs={'class': 'settings-input', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'settings-input'}),
            'city': forms.TextInput(attrs={'class': 'settings-input'}),
            'state': forms.TextInput(attrs={'class': 'settings-input'}),
        }

class AdminAddCustomerForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;',
        'placeholder': 'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;',
        'placeholder': 'customer@example.com'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;'
    }))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;'
    }))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;'
    }))
    postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px; border: 1px solid var(--line); background: var(--cream); border-radius: 6px;'
    }))

class AdminAddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'settings-input'}),
            'description': forms.Textarea(attrs={'class': 'settings-input', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'settings-input', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'settings-input'}),
            'status': forms.Select(attrs={'class': 'settings-input'}),
        }

class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ], widget=forms.Select(attrs={
        'style': 'padding: 4px 8px; border: 1px solid var(--line); border-radius: 6px;'
    }))