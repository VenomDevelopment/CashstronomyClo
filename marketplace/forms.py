from django import forms
from .models import Review, Order

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...', 'class': 'form-control'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'postal_code', 'country'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Last Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Phone Number', 'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'placeholder': 'Enter Street Address', 'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, etc. (optional)', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter City', 'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Enter ZIP Code', 'class': 'form-control'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter Country', 'class': 'form-control'}),
        }
