from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Pharmacy, PharmacyProduct, PharmacyChat, PharmacyChatMessage
from products.models import Product
from django.http import JsonResponse


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
    

@login_required
def pharmacy_chat(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk)
    chat, _ = PharmacyChat.objects.get_or_create(
        pharmacy=pharmacy,
        user=request.user
    )
    messages = PharmacyChatMessage.objects.filter(
        chat=chat
    ).order_by('created_at')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')
        if text or image:
            PharmacyChatMessage.objects.create(
                chat=chat,
                sender='user',
                text=text,
                image=image or ''
            )
        return redirect('pharmacy_chat', pk=pk)

    return render(request, 'pharmacy_chat.html', {
        'pharmacy': pharmacy,
        'chat': chat,
        'messages': messages,
    })


@login_required
def pharmacy_chat_api(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk)
    chat, _ = PharmacyChat.objects.get_or_create(
        pharmacy=pharmacy,
        user=request.user
    )
    last_id = request.GET.get('last_id', 0)
    msgs = PharmacyChatMessage.objects.filter(
        chat=chat,
        id__gt=last_id
    ).order_by('created_at')

    data = []
    for msg in msgs:
        data.append({
            'id': msg.pk,
            'sender': msg.sender,
            'text': msg.text,
            'image': msg.image.url if msg.image else None,
            'time': msg.created_at.strftime('%H:%M'),
        })
    return JsonResponse({'messages': data})


# Панель менеджера аптеки
@login_required
def manager_panel(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk, manager=request.user)
    chats = PharmacyChat.objects.filter(
        pharmacy=pharmacy
    ).order_by('-created_at')
    return render(request, 'manager_panel.html', {
        'pharmacy': pharmacy,
        'chats': chats,
    })


@login_required
def manager_chat(request, chat_pk):
    chat = get_object_or_404(
        PharmacyChat,
        pk=chat_pk,
        pharmacy__manager=request.user
    )
    messages = PharmacyChatMessage.objects.filter(
        chat=chat
    ).order_by('created_at')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')
        if text or image:
            PharmacyChatMessage.objects.create(
                chat=chat,
                sender='manager',
                text=text,
                image=image or ''
            )
        return redirect('manager_chat', chat_pk=chat_pk)

    return render(request, 'manager_chat.html', {
        'chat': chat,
        'messages': messages,
        'pharmacy': chat.pharmacy,
    })