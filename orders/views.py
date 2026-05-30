from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .telegram import send_order_notification




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