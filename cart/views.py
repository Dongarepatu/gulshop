from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    
    items = []
    for product_id, quantity in cart.cart.items():
        try:
            product = Product.objects.get(id=product_id)
            
            # FIX: Handle if quantity is dict or int
            if isinstance(quantity, dict):
                qty = quantity.get('quantity', 1)
            else:
                qty = quantity
            
            total_price = product.price * qty
            items.append({
                'product': product,
                'quantity': qty,
                'total': total_price
            })
        except Product.DoesNotExist:
            continue
    
    total_price = sum(item['total'] for item in items)
    total_items = sum(item['quantity'] for item in items)
    
    return render(request, 'cart/detail.html', {
        'cart_items': items,
        'total_price': total_price,
        'total_items': total_items
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart:cart_detail')

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    
    messages.success(request, f"{product.name} removed from cart!")
    return redirect('cart:cart_detail')

def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    
    messages.success(request, "Cart cleared!")
    return redirect('cart:cart_detail')