from django import forms
from products.models import Product


class AddOrderForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-20 px-3 py-2 border border-gray-300 rounded-md text-center text-sm focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'تعداد',
        })
    )

    class Meta:
        model = Product
        fields = []


class DiscountCodeForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        required=True,
        label='کد تخفیف',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف خود را وارد کنید'
        })
    )