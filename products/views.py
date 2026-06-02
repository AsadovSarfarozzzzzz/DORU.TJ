from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.http import JsonResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ProductView(LoginRequiredMixin,generic.ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)
    
class ProductAdd(LoginRequiredMixin,generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_add.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        return redirect('home')

class ProductDeleteView(LoginRequiredMixin,UserPassesTestMixin,generic.DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        self.object.delete()  # soft delete
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect(self.success_url)

class ProductUpdateView(generic.UpdateView):
    model = Product
    fields = '__all__'
    template_name = 'product_edit.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff

# @login_required
# def product_add(request):
#     if not request.user.is_staff:
#         return redirect('home')
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')
#     else:
#         form = ProductForm()
#     return render(request, 'product_add.html', {'form': form})

# @login_required
# def product_delete(request, pk):
#     if not request.user.is_staff:
#         return redirect('home')
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         product.delete()
#         return redirect('product_list')
#     return redirect('product_list')

# @login_required
# def product_edit(request,pk):
#     if not request.user.is_staff:
#         return redirect('home')
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')
#     else:
#         form = ProductForm(instance=product)
#     return render(request, 'product_edit.html', {'form': form})
    

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
    similar = Product.objects.filter(
        category=product.category
    ).exclude(pk=pk)[:4]
    return render(request, 'detail.html', {
        'product': product,
        'similar': similar
    })