from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .telegram import send_order_notification
from django.http import JsonResponse
from .models import Cart, CartItem, Order, OrderItem, DeliveryChat, DeliveryChatMessage, CourierLocation
import json

@login_required
def delivery_chat(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)
    chat, _ = DeliveryChat.objects.get_or_create(order=order)
    messages = DeliveryChatMessage.objects.filter(chat=chat).order_by('created_at')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')

        if text or image:
            DeliveryChatMessage.objects.create(
                chat=chat,
                sender='client',
                text=text,
                image=image or ''
            )
        return redirect('delivery_chat', order_pk=order_pk)

    return render(request, 'delivery_chat.html', {
        'order': order,
        'chat': chat,
        'messages': messages,
    })


@login_required
def chat_messages_api(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)
    chat, _ = DeliveryChat.objects.get_or_create(order=order)
    last_id = request.GET.get('last_id', 0)

    messages = DeliveryChatMessage.objects.filter(
        chat=chat,
        id__gt=last_id
    ).order_by('created_at')

    data = []
    for msg in messages:
        data.append({
            'id': msg.pk,
            'sender': msg.sender,
            'text': msg.text,
            'image': msg.image.url if msg.image else None,
            'time': msg.created_at.strftime('%H:%M'),
        })

    return JsonResponse({'messages': data})

@login_required
def courier_location_api(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)
    try:
        location = CourierLocation.objects.get(order=order)
        return JsonResponse({
            'lat': location.latitude,
            'lng': location.longitude,
            'updated_at': location.updated_at.strftime('%H:%M:%S')
        })
    except CourierLocation.DoesNotExist:
        return JsonResponse({'error': 'Локация недоступна'})

def update_courier_location(request, order_pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_pk)
        data = json.loads(request.body)
        CourierLocation.objects.update_or_create(
            order=order,
            defaults={
                'latitude': data['lat'],
                'longitude': data['lng'],
            }
        )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'})

def courier_send_message(request, order_pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_pk)
        chat, _ = DeliveryChat.objects.get_or_create(order=order)
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')

        if text or image:
            DeliveryChatMessage.objects.create(
                chat=chat,
                sender='courier',
                text=text,
                image=image or ''
            )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'{product.name} добавлен в корзину!')
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def update_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect('cart')

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart).select_related('product')
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart).select_related('product')
    
    if not items:
        messages.error(request, 'Корзина пуста!')
        return redirect('cart')

    if request.method == 'POST':
        address = request.POST.get('address')
        prescription = request.FILES.get('prescription')

        if not address:
            messages.error(request, 'Укажите адрес доставки!')
            return redirect('checkout')

        total = sum(item.product.price * item.quantity for item in items)
        order = Order.objects.create(
            user=request.user,
            address=address,
            total=total,
            prescription=prescription or ''
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        order_items = OrderItem.objects.filter(order=order)
        send_order_notification(order, order_items)
        # очищаем корзину
        items.delete()
        messages.success(request, 'Заказ оформлен!')
        return redirect('order_detail', pk=order.pk)

    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = OrderItem.objects.filter(order=order).select_related('product')
    return render(request, 'order_detail.html', {
        'order': order,
        'items': items
    })


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Заказ отменён!')
    else:
        messages.error(request, 'Этот заказ нельзя отменить!')
    return redirect('my_orders')


@login_required
def repeat_order(request, pk):
    old_order = get_object_or_404(Order, pk=pk, user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    for item in old_order.orderitem_set.all():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=item.product
        )
        if not created:
            cart_item.quantity += item.quantity
            cart_item.save()
    messages.success(request, 'Товары добавлены в корзину!')
    return redirect('cart')