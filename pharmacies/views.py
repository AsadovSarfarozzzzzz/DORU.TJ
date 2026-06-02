from django.shortcuts import get_object_or_404
from django.views import generic
from .models import Pharmacy, PharmacyProduct
from products.models import Product


class PharmacyListView(generic.ListView):
    model = Pharmacy
    template_name = 'pharmacy_list.html'
    context_object_name = 'pharmacies'

    def get_queryset(self):
        return Pharmacy.objects.filter(is_active=True)


class PharmacyDetailView(generic.DetailView):
    model = Pharmacy
    template_name = 'pharmacy_detail.html'
    context_object_name = 'pharmacy'

    def get_queryset(self):
        return Pharmacy.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = PharmacyProduct.objects.filter(
            pharmacy=self.object
        ).select_related('product')
        return context


class ProductPharmaciesView(generic.DetailView):
    model = Product
    template_name = 'product_pharmacies.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pharmacies'] = PharmacyProduct.objects.filter(
            product=self.object,
            pharmacy__is_active=True
        ).select_related('pharmacy').order_by('price')
        return context