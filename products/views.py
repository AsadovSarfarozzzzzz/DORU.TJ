from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, Category, Favorite
from .forms import ProductForm, CategoryForm
from django.http import JsonResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product, Category, Manufacturer, Review
from django.contrib.auth.decorators import login_required
from django.db import models
from orders.models import Order
from django.db.models import Avg

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
    popular = Product.objects.filter(stock__gt=0, is_deleted=False).order_by('-id')[:8]

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
    product = get_object_or_404(Product, pk=pk, is_deleted=False)
    similar = Product.objects.filter(
        category=product.category,
        is_deleted=False
    ).exclude(pk=pk)[:4]

    reviews = Review.objects.filter(product=product).order_by('-created_at')

    from django.db.models import Avg
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'detail.html', {
        'product': product,
        'similar': similar,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'user_review': user_review,
    })


@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        messages.success(request, f'{product.name} удалён из избранного')
    else:
        messages.success(request, f'{product.name} добавлен в избранное')
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'favorites.html', {'favorites': favorites})


from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta, date
from django.utils import timezone
import json


@login_required
def analytics(request):
    if not request.user.is_staff:
        return redirect('home')

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    orders_daily = Order.objects.filter(
        created_at__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id'),
        revenue=Sum('total')
    ).order_by('day')

    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    )

    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status__in=['done', 'delivering', 'confirmed']).aggregate(s=Sum('total'))['s'] or 0
    avg_order = Order.objects.filter(status__in=['done', 'delivering', 'confirmed']).aggregate(a=Avg('total'))['a'] or 0

    days = []
    counts = []
    revenues = []
    for entry in orders_daily:
        days.append(entry['day'].isoformat())
        counts.append(entry['count'])
        revenues.append(float(entry['revenue'] or 0))

    status_labels = []
    status_counts = []
    for entry in orders_by_status:
        status_labels.append(dict(Order.STATUS_CHOICES).get(entry['status'], entry['status']))
        status_counts.append(entry['count'])

    return render(request, 'analytics.html', {
        'days': json.dumps(days),
        'counts': json.dumps(counts),
        'revenues': json.dumps(revenues),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order': avg_order,
    })


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if rating:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': int(rating),
                    'comment': comment
                }
            )
    return redirect('product_detail', pk=pk)