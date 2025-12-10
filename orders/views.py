# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Order, OrderItem
import random
from datetime import datetime

def checkout(request):
    """
    Simple checkout page - NO ERRORS
    """
    cart = request.session.get('cart', {})
    
    # Check if cart is empty
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('products:cart_detail')
    
    # Get cart items with proper error handling
    cart_items = []
    total_amount = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            # Fix: Handle if quantity is dict or int
            if isinstance(quantity, dict):
                qty = quantity.get('quantity', 1)
            else:
                qty = quantity
                
            item_total = product.price * qty
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })
            total_amount += item_total
        except (Product.DoesNotExist, ValueError):
            continue
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        
        # Simple validation
        if not name or not phone or not address:
            messages.error(request, 'Please fill required fields!')
            return render(request, 'orders/create.html', {
                'cart_items': cart_items,
                'total_amount': total_amount
            })
        
        # Generate simple order ID
        order_id = f"ORD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        try:
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                order_id=order_id,
                name=name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                total_amount=total_amount,
                status='pending'
            )
            
            # Create order items
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=int(product_id))
                    if isinstance(quantity, dict):
                        qty = quantity.get('quantity', 1)
                    else:
                        qty = quantity
                        
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price
                    )
                except (Product.DoesNotExist, ValueError):
                    continue
            
            # Clear cart
            if 'cart' in request.session:
                del request.session['cart']
            
            # Redirect to success
            return redirect('orders:success', order_id=order.order_id)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'orders/create.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

def order_success(request, order_id):
    """
    Order success page
    """
    try:
        order = Order.objects.get(order_id=order_id)
        return render(request, 'orders/created.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, 'Order not found!')
        return redirect('products:home')

@login_required
def order_history(request):
    """
    View order history
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """
    View order details
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

def track_order(request, order_id):
    """
    Track order
    """
    try:
        order = Order.objects.get(order_id=order_id)
        return render(request, 'orders/track_order.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, 'Order not found!')
        return redirect('products:home')