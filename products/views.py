from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Manufacturer

def home(request):
    categories = Category.objects.all()
    popular = Product.objects.filter(stock__gt=0).order_by('-id')[:8]
    return render(request, 'products/home.html', {
        'categories': categories,
        'popular': popular
    })


def catalog(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    
    # фильтры
    category_slug = request.GET.get('category')
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    is_prescription = request.GET.get('is_prescription')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(name__icontains=search) | \
                   products.filter(active_substance__icontains=search)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if is_prescription:
        products = products.filter(is_prescription=True)

    return render(request, 'products/catalog.html', {
        'products': products,
        'categories': categories,
    })