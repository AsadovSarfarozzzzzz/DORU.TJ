from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Manufacturer

def home(request):
    categories = Category.objects.all()
    popular = Product.objects.filter(stock__gt=0).order_by('-id')[:8]
    return render(request, 'products/home.html', {
        'categories': categories,
        'popular': popular
    })