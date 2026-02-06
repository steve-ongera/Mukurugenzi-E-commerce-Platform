"""
Mukurugenzi E-commerce Platform - URL Configuration
URL patterns for all views
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================================
    # HOME & PRODUCTS
    # ============================================================================
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('api/get-variant-details/', views.get_variant_details, name='get_variant_details'),
    
    # ============================================================================
    # CART
    # ============================================================================
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # ============================================================================
    # CHECKOUT & ORDERS
    # ============================================================================
    path('checkout/', views.checkout, name='checkout'),
    path('api/calculate-delivery-fee/', views.calculate_delivery_fee, name='calculate_delivery_fee'),
    path('place-order/', views.place_order, name='place_order'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # ============================================================================
    # PAYMENTS - M-PESA
    # ============================================================================
    path('payment/mpesa/<int:order_id>/', views.mpesa_payment, name='mpesa_payment'),
    path('payment/mpesa/<int:order_id>/initiate/', views.initiate_mpesa_stk_push, name='initiate_mpesa_stk_push'),
    path('payment/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # ============================================================================
    # PAYMENTS - PAYPAL
    # ============================================================================
    path('payment/paypal/<int:order_id>/', views.paypal_payment, name='paypal_payment'),
    path('payment/paypal/<int:order_id>/create/', views.paypal_create_payment, name='paypal_create_payment'),
    path('payment/paypal/<int:order_id>/execute/', views.paypal_execute, name='paypal_execute'),
    path('payment/paypal/<int:order_id>/cancel/', views.paypal_cancel, name='paypal_cancel'),
    
    # ============================================================================
    # ORDER MANAGEMENT
    # ============================================================================
    path('orders/', views.orders, name='orders'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('order/<str:order_number>/track/', views.track_order, name='track_order'),
    
    # ============================================================================
    # AUTHENTICATION
    # ============================================================================
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    
    # ============================================================================
    # USER PROFILE
    # ============================================================================
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
]