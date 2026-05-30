from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'category',
                  'manufacturer', 'image', 'description',
                  'active_substance', 'is_prescription']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Цена'}),
            'stock': forms.NumberInput(attrs={'placeholder': '0'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 3}),
            'active_substance': forms.TextInput(attrs={'placeholder': 'Действующее вещество'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder' : 'Cotegory name'}),
            'slug': forms.TextInput(attrs={'placeholder' : 'Example: Vitamin, Pain and etc.'}),
        }