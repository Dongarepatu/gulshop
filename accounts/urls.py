from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SignUpView, profile_view, wishlist_view, 
    ProfileUpdateView, add_to_wishlist, remove_from_wishlist, clear_wishlist
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Profile and wishlist URLs
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/clear/', clear_wishlist, name='clear_wishlist'),
]