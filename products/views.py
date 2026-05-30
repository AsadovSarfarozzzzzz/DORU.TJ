from django.shortcuts import  redirect ,render, get_object_or_404
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required

@login_required
def product_list(request):
    if not request.user.is_staff:
        return redirect('home')
    products = Product.objects.all()
    return render(request, 'product_list.html',{'product':products})

@login_required
def product_add(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_add.html', {'form': form})



def home(request):
    categories = Category.objects.all()
    popular = Product.objects.filter(stock__gt=0).order_by('-id')[:8]

    advantages = [
        {"icon": "🚚", "title": "Быстрая доставка", "desc": "За 2 часа по Душанбе"},
        {"icon": "🤖", "title": "AI Консультант", "desc": "Подберём лекарство по симптомам"},
        {"icon": "💰", "title": "Выгодные цены", "desc": "Лучшие цены в городе"},
        {"icon": "🔒", "title": "Безопасно", "desc": "Только сертифицированные препараты"},
    ]
    return render(request, 'home.html', {
        'categories': categories,
        'popular': popular,
        'advantages': advantages
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

    return render(request, 'catalog.html', {
        'products': products,
        'categories': categories,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # аналоги — те же категории
    similar = Product.objects.filter(
        category=product.category
    ).exclude(pk=pk)[:4]
    return render(request, 'detail.html', {
        'product': product,
        'similar': similar
    })