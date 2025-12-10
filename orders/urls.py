# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Use 'create' to match your template name
    path('create/', views.checkout, name='create'),
    path('success/<str:order_id>/', views.order_success, name='success'),
    path('history/', views.order_history, name='history'),  
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('track/<str:order_id>/', views.track_order, name='track'),
]