from django import forms
from .models import Customer_details
from django.core.validators import RegexValidator

class CustomerForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Customer_details
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False  # phone is optional
