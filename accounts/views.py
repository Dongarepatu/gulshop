from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def wishlist_view(request):
    """User wishlist view"""
    # For now, we'll use session-based wishlist. You can modify this later for database storage.
    wishlist_items = request.session.get('wishlist', [])
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/wishlist.html', context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit profile view"""
    model = CustomUser
    template_name = 'accounts/edit_profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist (session-based)"""
    if 'wishlist' not in request.session:
        request.session['wishlist'] = []
    
    wishlist = request.session['wishlist']
    
    # Check if product is already in wishlist
    if product_id not in wishlist:
        wishlist.append(product_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True
        messages.success(request, 'Product added to wishlist!')
    else:
        messages.info(request, 'Product already in wishlist!')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    if 'wishlist' in request.session:
        wishlist = request.session['wishlist']
        if str(product_id) in wishlist:
            wishlist.remove(str(product_id))
            request.session['wishlist'] = wishlist
            request.session.modified = True
            messages.success(request, 'Product removed from wishlist!')
    
    return redirect('wishlist')

@login_required
def clear_wishlist(request):
    """Clear all items from wishlist"""
    if 'wishlist' in request.session:
        request.session['wishlist'] = []
        request.session.modified = True
        messages.success(request, 'Wishlist cleared successfully!')
    
    return redirect('wishlist')