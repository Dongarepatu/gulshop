# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category

def home_view(request):
    """Home page view"""
    featured_products = Product.objects.filter(available=True)[:4]
    categories = Category.objects.all()
    
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'title': 'Home - Premium Jaggery Shop'
    })

def product_detail(request, id, slug):
    """Product detail view"""
    product = get_object_or_404(Product, id=id, slug=slug)
    
    # Check if product is in wishlist
    is_in_wishlist = False
    if request.user.is_authenticated:
        # Check session-based wishlist
        if 'wishlist' in request.session:
            wishlist_items = request.session['wishlist']
            if isinstance(wishlist_items, list) and str(product.id) in wishlist_items:
                is_in_wishlist = True
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'is_in_wishlist': is_in_wishlist
    })

def product_list(request, category_slug=None):
    """Product list view"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

# ===== CART FUNCTIONS =====
def add_to_cart(request, product_id):
    """
    Add product to cart (session-based)
    Supports both POST (Add to Cart) and GET (Buy Now)
    """
    try:
        # Get product first
        product = get_object_or_404(Product, id=product_id)
        
        # Get quantity from request
        if request.method == 'POST':
            # From Add to Cart form
            quantity = int(request.POST.get('quantity', 1))
        else:
            # From Buy Now link (GET request)
            quantity = int(request.GET.get('quantity', 1))
        
        # Validate quantity
        if quantity < 1 or quantity > 10:
            messages.error(request, 'Quantity must be between 1 and 10')
            return redirect('products:product_detail', id=product_id, slug=product.slug)
        
        # Get or initialize cart in session
        cart = request.session.get('cart', {})
        
        # Add product to cart - STORE AS INTEGER
        product_key = str(product_id)
        
        # FIX: Handle if cart item is dictionary (old format)
        if product_key in cart:
            if isinstance(cart[product_key], dict):
                # If it's a dictionary, get quantity from it
                old_quantity = cart[product_key].get('quantity', 0)
                cart[product_key] = old_quantity + quantity
            else:
                # If it's an integer, add normally
                cart[product_key] += quantity
        else:
            # New item, store as integer
            cart[product_key] = quantity
        
        # Save cart to session
        request.session['cart'] = cart
        request.session.modified = True
        
        messages.success(request, f'✅ Added {quantity} {product.name} to cart!')
        
        # Check if it's a Buy Now request
        if request.method == 'GET' and request.GET.get('buy_now'):
            # Redirect to cart page for checkout
            return redirect('products:cart_detail')
        else:
            # Redirect back to product page
            return redirect('products:product_detail', id=product_id, slug=product.slug)
            
    except (ValueError, KeyError) as e:
        messages.error(request, 'Invalid quantity')
        try:
            return redirect('products:product_detail', id=product_id, slug=product.slug)
        except:
            return redirect('products:product_list')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('products:product_list')

def cart_detail(request):
    """
    Display cart items - FIXED VERSION
    """
    cart = request.session.get('cart', {})
    
    # Get products from cart
    cart_items = []
    total_price = 0
    total_items = 0
    
    for product_id, cart_item in cart.items():  # Changed 'quantity' to 'cart_item'
        try:
            product = Product.objects.get(id=int(product_id))
            
            # FIX: Check if cart_item is dict or int
            if isinstance(cart_item, dict):
                # If it's a dictionary, get quantity from it
                quantity = cart_item.get('quantity', 1)
            else:
                # If it's an integer, use directly
                quantity = cart_item
            
            # Calculate item total
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total_price += item_total
            total_items += quantity
        except (Product.DoesNotExist, ValueError):
            # Remove invalid product from cart
            cart.pop(product_id, None)
    
    # Update session if invalid products were removed
    if cart:
        request.session['cart'] = cart
        request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
    }
    
    return render(request, 'cart/detail.html', context)

def remove_from_cart(request, product_id):
    """
    Remove item from cart
    """
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        try:
            product = Product.objects.get(id=product_id)
            messages.info(request, f'Removed {product.name} from cart')
        except Product.DoesNotExist:
            messages.info(request, 'Item removed from cart')
        
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('products:cart_detail')

def clear_cart(request):
    """
    Clear all items from cart
    """
    if 'cart' in request.session:
        del request.session['cart']
        messages.info(request, 'Cart cleared')
    
    return redirect('products:cart_detail')

def update_cart_quantity(request, product_id):
    """
    Update quantity of a cart item
    """
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_key = str(product_id)
        
        action = request.POST.get('update')
        
        if product_key in cart:
            # Get current quantity
            if isinstance(cart[product_key], dict):
                current_qty = cart[product_key].get('quantity', 1)
            else:
                current_qty = cart[product_key]
            
            # Update based on action
            if action == 'increase':
                new_qty = current_qty + 1
                if new_qty <= 10:
                    cart[product_key] = new_qty
            elif action == 'decrease':
                new_qty = current_qty - 1
                if new_qty >= 1:
                    cart[product_key] = new_qty
                else:
                    # Remove if quantity becomes 0
                    del cart[product_key]
            
            request.session['cart'] = cart
            request.session.modified = True
    
    return redirect('products:cart_detail')