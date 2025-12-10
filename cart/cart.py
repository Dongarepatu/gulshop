from django.conf import settings

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, product, quantity=1):
        product_id = str(product.id)
        
        # ALWAYS store as simple integer (not dictionary)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        
        self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
            self.save()