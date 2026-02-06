"""
Mukurugenzi E-commerce Platform - Function-Based Views
Complete views for products, cart, checkout, payments, orders, and authentication
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Min, Max, Prefetch
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from decimal import Decimal
import json
import requests
import base64
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import *


# ============================================================================
# HOME & PRODUCT VIEWS
# ============================================================================

def index(request):
    """Homepage with featured products and videos"""
    
    # Get active banners
    banners = Banner.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
    ).order_by('order')[:5]
    
    # Featured products
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category', 'brand').prefetch_related(
        'images',
        Prefetch('reviews', queryset=ProductReview.objects.filter(is_approved=True))
    )[:8]
    
    # New arrivals (last 30 days)
    new_products = Product.objects.filter(
        is_active=True,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).select_related('category', 'brand').prefetch_related('images').order_by('-created_at')[:12]
    
    # If not enough new products, get latest products
    if new_products.count() < 12:
        new_products = Product.objects.filter(
            is_active=True
        ).select_related('category', 'brand').prefetch_related('images').order_by('-created_at')[:12]
    
    # Featured videos
    featured_videos = Video.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related('genres')[:6]
    
    # Get categories (parent categories only)
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('subcategories')[:5]
    
    # Calculate date 7 days ago for "New" badge
    today_minus_7 = timezone.now() - timedelta(days=7)
    
    # Get cart count for current user
    cart = get_or_create_cart(request)
    cart_count = cart.total_items if cart else 0
    
    context = {
        'banners': banners,
        'featured_products': featured_products,
        'new_products': new_products,
        'featured_videos': featured_videos,
        'categories': categories,
        'today_minus_7': today_minus_7,
        'cart_count': cart_count,
    }
    
    return render(request, 'store/index.html', context)


def products(request):
    """Product listing with filters and search"""
    
    # Base queryset
    products_list = Product.objects.filter(
        is_active=True
    ).select_related('category', 'brand').prefetch_related(
        'images', 
        Prefetch('variants', queryset=ProductVariant.objects.filter(is_active=True))
    )
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        # Get category and all its subcategories
        category_ids = [selected_category.id]
        category_ids.extend(selected_category.subcategories.values_list('id', flat=True))
        products_list = products_list.filter(category_id__in=category_ids)
    
    # Brand filter
    brand_slug = request.GET.get('brand', '')
    selected_brand = None
    if brand_slug:
        selected_brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
        products_list = products_list.filter(brand=selected_brand)
    
    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products_list = products_list.filter(base_price__gte=Decimal(min_price))
    if max_price:
        products_list = products_list.filter(base_price__lte=Decimal(max_price))
    
    # Product type filter
    product_type = request.GET.get('type', '')
    if product_type:
        products_list = products_list.filter(product_type=product_type)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products_list = products_list.order_by('base_price')
    elif sort_by == 'price_high':
        products_list = products_list.order_by('-base_price')
    elif sort_by == 'name':
        products_list = products_list.order_by('name')
    else:  # newest
        products_list = products_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products_list, 12)  # 12 products per page
    page_number = request.GET.get('page', 1)
    products_page = paginator.get_page(page_number)
    
    # Get all categories and brands for filters
    all_categories = Category.objects.filter(is_active=True, parent__isnull=True)
    all_brands = Brand.objects.filter(is_active=True)
    
    # Get cart count
    cart = get_or_create_cart(request)
    cart_count = cart.total_items if cart else 0
    
    context = {
        'products': products_page,
        'categories': all_categories,
        'brands': all_brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'search_query': search_query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'product_type': product_type,
        'cart_count': cart_count,
    }
    
    return render(request, 'store/products.html', context)



def product_detail(request, slug):
    """Product detail page with variants"""
    
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related(
            'images',
            Prefetch('variants', queryset=ProductVariant.objects.filter(is_active=True).select_related('size', 'color'))
        ),
        slug=slug,
        is_active=True
    )
    
    # Get available sizes and colors
    available_sizes = Size.objects.filter(
        productvariant__product=product,
        productvariant__is_active=True
    ).distinct().order_by('order')
    
    available_colors = Color.objects.filter(
        productvariant__product=product,
        productvariant__is_active=True
    ).distinct()
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user').prefetch_related('images')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]
    
    # Get cart count
    cart = get_or_create_cart(request)
    cart_count = cart.total_items if cart else 0
    
    context = {
        'product': product,
        'available_sizes': available_sizes,
        'available_colors': available_colors,
        'reviews': reviews,
        'average_rating': average_rating,
        'related_products': related_products,
        'cart_count': cart_count,
    }
    
    return render(request, 'store/product_detail.html', context)


@require_POST
def get_variant_details(request):
    """AJAX endpoint to get variant details based on size and color selection"""
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size_id = data.get('size_id')
        color_id = data.get('color_id')
        
        variant = ProductVariant.objects.filter(
            product_id=product_id,
            size_id=size_id,
            color_id=color_id,
            is_active=True
        ).first()
        
        if variant:
            return JsonResponse({
                'success': True,
                'variant_id': variant.id,
                'sku': variant.sku,
                'price': str(variant.price),
                'compare_at_price': str(variant.compare_at_price) if variant.compare_at_price else None,
                'stock_quantity': variant.stock_quantity,
                'is_in_stock': variant.is_in_stock,
                'is_low_stock': variant.is_low_stock,
                'variant_image': variant.variant_image.url if variant.variant_image else None,
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Variant not available'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ============================================================================
# CART VIEWS
# ============================================================================


def get_or_create_cart(request):
    """Helper function to get or create cart for user or session"""
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


@require_POST
def add_to_cart(request):
    """Add item to cart or update quantity"""
    
    try:
        data = json.loads(request.body)
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1'
            }, status=400)
        
        variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
        
        # Check stock
        if variant.stock_quantity < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {variant.stock_quantity} items available in stock'
            }, status=400)
        
        cart = get_or_create_cart(request)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if new_quantity > variant.stock_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot add more. Only {variant.stock_quantity} items available'
                }, status=400)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart_count': cart.total_items,
            'cart_subtotal': str(cart.subtotal)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)



@require_POST
def update_cart_item(request):
    """Update cart item quantity"""
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1'
            }, status=400)
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        if quantity > cart_item.product_variant.stock_quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {cart_item.product_variant.stock_quantity} items available'
            }, status=400)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
            'item_total': str(cart_item.total_price),
            'cart_subtotal': str(cart.subtotal),
            'cart_count': cart.total_items
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_count': cart.total_items,
            'cart_subtotal': str(cart.subtotal)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def cart(request):
    """View cart"""
    
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related(
        'product_variant__product',
        'product_variant__size',
        'product_variant__color'
    ).prefetch_related('product_variant__product__images')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'store/cart.html', context)


# ============================================================================
# CHECKOUT VIEWS
# ============================================================================

@login_required
def checkout(request):
    """Checkout page"""
    
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related(
        'product_variant__product',
        'product_variant__size',
        'product_variant__color'
    )
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product_variant.stock_quantity:
            messages.error(
                request,
                f'{item.product_variant.product.name} has only {item.product_variant.stock_quantity} items in stock'
            )
            return redirect('cart')
    
    # Get delivery options
    if request.user.is_international:
        delivery_options = InternationalShippingZone.objects.filter(is_active=True)
    else:
        counties = County.objects.filter(is_active=True).prefetch_related(
            Prefetch('delivery_stations', queryset=DeliveryStation.objects.filter(is_active=True))
        )
        delivery_options = counties
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'delivery_options': delivery_options,
        'is_international': request.user.is_international,
    }
    
    return render(request, 'store/checkout.html', context)


@login_required
@require_POST
def calculate_delivery_fee(request):
    """AJAX endpoint to calculate delivery fee"""
    
    try:
        data = json.loads(request.body)
        is_international = data.get('is_international', False)
        
        if is_international:
            zone_id = data.get('zone_id')
            zone = get_object_or_404(InternationalShippingZone, id=zone_id, is_active=True)
            delivery_fee = zone.shipping_cost
        else:
            station_id = data.get('station_id')
            station = get_object_or_404(DeliveryStation, id=station_id, is_active=True)
            delivery_fee = station.delivery_fee
        
        cart = get_or_create_cart(request)
        total = cart.subtotal + delivery_fee
        
        return JsonResponse({
            'success': True,
            'delivery_fee': str(delivery_fee),
            'subtotal': str(cart.subtotal),
            'total': str(total)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def place_order(request):
    """Process order and initiate payment"""
    
    try:
        cart = get_or_create_cart(request)
        cart_items = cart.items.select_related('product_variant')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty')
            return redirect('cart')
        
        # Get form data
        payment_method = request.POST.get('payment_method')
        customer_notes = request.POST.get('customer_notes', '')
        
        # Delivery details
        is_international = request.user.is_international
        delivery_type = 'international' if is_international else 'local'
        
        if is_international:
            zone_id = request.POST.get('shipping_zone')
            shipping_zone = get_object_or_404(InternationalShippingZone, id=zone_id, is_active=True)
            delivery_fee = shipping_zone.shipping_cost
            shipping_address = request.POST.get('shipping_address')
            shipping_phone = request.POST.get('shipping_phone')
            
            delivery_station = None
        else:
            station_id = request.POST.get('delivery_station')
            delivery_station = get_object_or_404(DeliveryStation, id=station_id, is_active=True)
            delivery_fee = delivery_station.delivery_fee
            shipping_zone = None
            shipping_address = delivery_station.address
            shipping_phone = request.user.phone_number
        
        # Calculate totals
        subtotal = cart.subtotal
        total_amount = subtotal + delivery_fee
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            status='pending',
            delivery_type=delivery_type,
            delivery_station=delivery_station,
            shipping_zone=shipping_zone,
            shipping_address=shipping_address,
            shipping_phone=shipping_phone,
            customer_notes=customer_notes
        )
        
        # Create order items
        for item in cart_items:
            variant = item.product_variant
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                product_name=variant.product.name,
                variant_details=f"Size: {variant.size.name if variant.size else 'N/A'}, Color: {variant.color.name if variant.color else 'N/A'}",
                quantity=item.quantity,
                unit_price=variant.price,
                total_price=item.total_price
            )
            
            # Reduce stock
            variant.stock_quantity -= item.quantity
            variant.save()
        
        # Create order status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created',
            created_by=request.user
        )
        
        # Clear cart
        cart_items.delete()
        
        # Redirect to payment based on method
        if payment_method == 'mpesa':
            return redirect('mpesa_payment', order_id=order.id)
        elif payment_method == 'paypal':
            return redirect('paypal_payment', order_id=order.id)
        else:
            messages.error(request, 'Invalid payment method')
            return redirect('checkout')
            
    except Exception as e:
        messages.error(request, f'Error placing order: {str(e)}')
        return redirect('checkout')


# ============================================================================
# PAYMENT VIEWS - M-PESA
# ============================================================================

@login_required
def mpesa_payment(request, order_id):
    """M-Pesa payment page"""
    
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    
    context = {
        'order': order,
    }
    
    return render(request, 'store/mpesa_payment.html', context)


@login_required
@require_POST
def initiate_mpesa_stk_push(request, order_id):
    """Initiate M-Pesa STK Push"""
    
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
        phone_number = request.POST.get('phone_number')
        
        # Format phone number (remove +254 or 0 and add 254)
        if phone_number.startswith('+254'):
            phone_number = phone_number[1:]
        elif phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        # M-Pesa API credentials (from settings or environment variables)
        from django.conf import settings
        
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        callback_url = settings.MPESA_CALLBACK_URL
        
        # Use sandbox or production
        if settings.MPESA_ENVIRONMENT == 'sandbox':
            auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        else:
            auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            stk_push_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        # Get access token
        auth_response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
        access_token = auth_response.json().get('access_token')
        
        # Prepare STK Push request
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(order.total_amount),
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": order.order_number,
            "TransactionDesc": f"Payment for Order {order.order_number}"
        }
        
        # Make STK Push request
        response = requests.post(stk_push_url, json=payload, headers=headers)
        response_data = response.json()
        
        if response_data.get('ResponseCode') == '0':
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                payment_method='mpesa',
                amount=order.total_amount,
                currency='KES',
                status='processing',
                transaction_id=response_data.get('CheckoutRequestID'),
                mpesa_phone=phone_number,
                gateway_response=response_data
            )
            
            messages.success(request, 'Payment request sent. Please check your phone to complete payment.')
            return redirect('order_confirmation', order_id=order.id)
        else:
            messages.error(request, f"Payment initiation failed: {response_data.get('errorMessage', 'Unknown error')}")
            return redirect('mpesa_payment', order_id=order.id)
            
    except Exception as e:
        messages.error(request, f'Error initiating payment: {str(e)}')
        return redirect('mpesa_payment', order_id=order.id)


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """M-Pesa payment callback"""
    
    try:
        data = json.loads(request.body)
        callback_data = data.get('Body', {}).get('stkCallback', {})
        
        result_code = callback_data.get('ResultCode')
        checkout_request_id = callback_data.get('CheckoutRequestID')
        
        # Find payment
        payment = Payment.objects.filter(transaction_id=checkout_request_id).first()
        
        if not payment:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Payment not found"})
        
        if result_code == 0:
            # Payment successful
            callback_metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract M-Pesa receipt number
            mpesa_receipt = None
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt = item.get('Value')
                    break
            
            payment.status = 'completed'
            payment.mpesa_receipt = mpesa_receipt
            payment.paid_at = timezone.now()
            payment.gateway_response = callback_data
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'confirmed'
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='confirmed',
                notes=f'Payment completed via M-Pesa. Receipt: {mpesa_receipt}'
            )
            
        else:
            # Payment failed
            payment.status = 'failed'
            payment.failure_reason = callback_data.get('ResultDesc', 'Payment failed')
            payment.gateway_response = callback_data
            payment.save()
        
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
        
    except Exception as e:
        return JsonResponse({"ResultCode": 1, "ResultDesc": str(e)})


# ============================================================================
# PAYMENT VIEWS - PAYPAL
# ============================================================================

@login_required
def paypal_payment(request, order_id):
    """PayPal payment page"""
    
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    
    # Convert KES to USD (you should use a real exchange rate API)
    # For demo purposes, using a fixed rate
    exchange_rate = 0.0078  # 1 KES = 0.0078 USD (approximate)
    amount_usd = float(order.total_amount) * exchange_rate
    
    context = {
        'order': order,
        'amount_usd': round(amount_usd, 2),
    }
    
    return render(request, 'store/paypal_payment.html', context)


@login_required
@require_POST
def paypal_create_payment(request, order_id):
    """Create PayPal payment"""
    
    try:
        from django.conf import settings
        import paypalrestsdk
        
        order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,  # sandbox or live
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        
        # Convert KES to USD
        exchange_rate = 0.0078
        amount_usd = float(order.total_amount) * exchange_rate
        
        # Create payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('paypal_execute', kwargs={'order_id': order.id})),
                "cancel_url": request.build_absolute_uri(reverse('paypal_cancel', kwargs={'order_id': order.id}))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Order {order.order_number}",
                        "sku": order.order_number,
                        "price": f"{amount_usd:.2f}",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{amount_usd:.2f}",
                    "currency": "USD"
                },
                "description": f"Payment for Order {order.order_number}"
            }]
        })
        
        if payment.create():
            # Save payment record
            Payment.objects.create(
                order=order,
                user=request.user,
                payment_method='paypal',
                amount=order.total_amount,
                currency='USD',
                status='processing',
                paypal_transaction_id=payment.id,
                gateway_response={'payment_id': payment.id}
            )
            
            # Redirect to PayPal
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            messages.error(request, f"PayPal payment creation failed: {payment.error}")
            return redirect('paypal_payment', order_id=order.id)
            
    except Exception as e:
        messages.error(request, f'Error creating PayPal payment: {str(e)}')
        return redirect('paypal_payment', order_id=order.id)


@login_required
def paypal_execute(request, order_id):
    """Execute PayPal payment after user approval"""
    
    try:
        import paypalrestsdk
        from django.conf import settings
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Payment successful
            payment_record = Payment.objects.filter(
                order=order,
                paypal_transaction_id=payment_id
            ).first()
            
            if payment_record:
                payment_record.status = 'completed'
                payment_record.paid_at = timezone.now()
                payment_record.gateway_response = payment.to_dict()
                payment_record.save()
            
            # Update order
            order.status = 'confirmed'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='confirmed',
                notes='Payment completed via PayPal'
            )
            
            messages.success(request, 'Payment completed successfully!')
            return redirect('order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Payment execution failed')
            return redirect('paypal_payment', order_id=order.id)
            
    except Exception as e:
        messages.error(request, f'Error executing payment: {str(e)}')
        return redirect('paypal_payment', order_id=order.id)


@login_required
def paypal_cancel(request, order_id):
    """Handle PayPal payment cancellation"""
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.warning(request, 'Payment was cancelled')
    return redirect('paypal_payment', order_id=order.id)


# ============================================================================
# ORDER VIEWS
# ============================================================================

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    
    order = get_object_or_404(
        Order.objects.select_related('delivery_station', 'shipping_zone').prefetch_related('items'),
        id=order_id,
        user=request.user
    )
    
    context = {
        'order': order,
    }
    
    return render(request, 'store/order_confirmation.html', context)


@login_required
def orders(request):
    """User's order history"""
    
    orders_list = Order.objects.filter(
        user=request.user
    ).select_related('delivery_station', 'shipping_zone').prefetch_related('items').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page', 1)
    orders_page = paginator.get_page(page_number)
    
    context = {
        'orders': orders_page,
    }
    
    return render(request, 'store/orders.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail page"""
    
    order = get_object_or_404(
        Order.objects.select_related('delivery_station', 'shipping_zone').prefetch_related(
            'items__product_variant',
            'status_history',
            'payments'
        ),
        order_number=order_number,
        user=request.user
    )
    
    context = {
        'order': order,
    }
    
    return render(request, 'store/order_detail.html', context)


@login_required
def track_order(request, order_number):
    """Order tracking page"""
    
    order = get_object_or_404(
        Order.objects.select_related('delivery_station', 'shipping_zone').prefetch_related('status_history'),
        order_number=order_number,
        user=request.user
    )
    
    # Define order status flow
    status_flow = [
        {'status': 'pending', 'label': 'Order Placed', 'icon': 'shopping-cart'},
        {'status': 'confirmed', 'label': 'Payment Confirmed', 'icon': 'check-circle'},
        {'status': 'processing', 'label': 'Processing', 'icon': 'cog'},
        {'status': 'shipped', 'label': 'Shipped', 'icon': 'truck'},
        {'status': 'delivered', 'label': 'Delivered', 'icon': 'home'},
    ]
    
    # Get current status index
    current_index = 0
    for i, step in enumerate(status_flow):
        if step['status'] == order.status:
            current_index = i
            break
    
    context = {
        'order': order,
        'status_flow': status_flow,
        'current_index': current_index,
    }
    
    return render(request, 'store/track_order.html', context)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register(request):
    """User registration"""
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_international = request.POST.get('is_international') == 'on'
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'store/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'store/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'store/register.html')
        
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered')
            return render(request, 'store/register.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                is_international=is_international
            )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'store/register.html')
    
    return render(request, 'store/register.html')


def user_login(request):
    """User login (supports email or username)"""
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        login_input = request.POST.get('login_input')  # Can be email or username
        password = request.POST.get('password')
        
        # Try to find user by email or username
        user = None
        if '@' in login_input:
            # Login with email
            try:
                user_obj = User.objects.get(email=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Login with username
            user = authenticate(request, username=login_input, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Merge session cart with user cart if exists
            session_key = request.session.session_key
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key).first()
                if session_cart:
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    
                    # Move items from session cart to user cart
                    for item in session_cart.items.all():
                        user_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product_variant=item.product_variant,
                            defaults={'quantity': item.quantity}
                        )
                        if not created:
                            user_item.quantity += item.quantity
                            user_item.save()
                    
                    # Delete session cart
                    session_cart.delete()
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next page or home
            next_page = request.GET.get('next', 'index')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid email/username or password')
    
    return render(request, 'store/login.html')


@login_required
def user_logout(request):
    """User logout"""
    
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('index')


def forgot_password(request):
    """Forgot password - send reset email"""
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.core.mail import send_mail
            from django.conf import settings
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Send email
            subject = 'Password Reset - Mukurugenzi'
            message = f'''
Hello {user.first_name or user.username},

You requested to reset your password. Click the link below to reset your password:

{reset_url}

If you didn't request this, please ignore this email.

This link will expire in 24 hours.

Best regards,
Mukurugenzi Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
    
    return render(request, 'store/forgot_password.html')


def reset_password(request, uidb64, token):
    """Reset password with token"""
    
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match')
            else:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password reset successful! Please login with your new password.')
                return redirect('login')
        
        context = {
            'validlink': True,
            'uidb64': uidb64,
            'token': token,
        }
        return render(request, 'store/reset_password.html', context)
    else:
        messages.error(request, 'Password reset link is invalid or has expired')
        return redirect('forgot_password')


# ============================================================================
# USER PROFILE VIEWS
# ============================================================================

@login_required
def profile(request):
    """User profile page"""
    
    if request.method == 'POST':
        # Update profile
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.phone_number = request.POST.get('phone_number', '')
        request.user.address = request.POST.get('address', '')
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            request.user.profile_image = request.FILES['profile_image']
        
        request.user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    # Get user statistics
    total_orders = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(
        user=request.user,
        status__in=['confirmed', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'store/profile.html', context)


@login_required
@require_POST
def change_password(request):
    """Change password"""
    
    old_password = request.POST.get('old_password')
    new_password1 = request.POST.get('new_password1')
    new_password2 = request.POST.get('new_password2')
    
    if not request.user.check_password(old_password):
        messages.error(request, 'Current password is incorrect')
        return redirect('profile')
    
    if new_password1 != new_password2:
        messages.error(request, 'New passwords do not match')
        return redirect('profile')
    
    request.user.set_password(new_password1)
    request.user.save()
    
    # Keep user logged in after password change
    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, request.user)
    
    messages.success(request, 'Password changed successfully')
    return redirect('profile')


from django.shortcuts import render

def custom_bad_request(request, exception):
    return render(request, 'errors/400.html', status=400)

def custom_permission_denied(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_server_error(request):
    return render(request, 'errors/500.html', status=500)
