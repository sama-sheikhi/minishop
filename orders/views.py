from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from django.contrib import messages

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.total_price
    return render(request, 'cart.html', {'cart_items': items, 'total_price': total})

def update_cart(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_')[1]
                try:
                    item = CartItem.objects.get(id=item_id, cart__user=request.user)
                    item.quantity = int(value)
                    item.save()
                except CartItem.DoesNotExist:
                    pass
        messages.success(request, "Your cart has been updated successfully!")
    return redirect('cart')

@login_required
def add_to_cart(request, product_id):
    from shop.models import Product
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{product.name}" added to your cart!')
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        messages.error(request, "Your shopping cart is empty!")
        return redirect('cart')
    cart_items = cart.items.all()
    total_price = cart.total_price

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()

        if not (full_name and address and phone):
            messages.error(request, "Full name, address, and phone are required!")
            return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

        stock_issues = [item.product.name for item in cart_items if item.quantity > item.product.stock]
        if stock_issues:
            messages.error(request, f"Insufficient stock for the following products: {', '.join(stock_issues)}")
            return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            phone=phone,
            additional_info=additional_info,
            total_amount=total_price
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete()
        messages.success(request, f"Order #{order.id} has been successfully placed!")
        return redirect('home')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def orders_list(request):
    if request.user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)
    return render(request, "orders_list.html", {"orders": orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_detail.html', {'order': order})