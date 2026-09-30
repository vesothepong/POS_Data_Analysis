from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "price", "stock_quantity", "reorder_level", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Iced Vanilla Latte, Artisan Sandwich"}),
            "category": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Beverages, Food, Bakery"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "reorder_level": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


class StockUpdateForm(forms.Form):
    stock_quantity = forms.IntegerField(
        min_value=0,
        max_value=10_000_000,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"})
    )
