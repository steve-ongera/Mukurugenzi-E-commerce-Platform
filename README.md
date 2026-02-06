# Mukurugenzi E-commerce Platform - Django Models

A professional, feature-rich e-commerce platform combining physical product sales (clothing, footwear, electronics) with Netflix-style video streaming capabilities.

## 🚀 Key Features

### Product Management
- **Multi-category products**: Shoes, Shirts, Electronics, Caps, Tote Bags, etc.
- **Size and color-based pricing**: Each size/color combination has its own price and stock
- **Comprehensive product variants**: Different prices for S, M, L, XL, different shoe sizes (40, 41, 42, etc.)
- **Brand management**: Associate products with brands
- **Multiple product images**: Primary and additional images per product
- **Inventory tracking**: Real-time stock management with low stock alerts

### Video Streaming (Netflix-style)
- **Multiple content types**: Movies, TV Series, Documentaries, Short Films, Video Clips
- **One-time rental**: User pays once and can watch once
- **Purchase option**: Unlimited viewing after purchase
- **Watch Later**: Users can save videos to watch later
- **Subscription plans**: Monthly/yearly subscriptions with different access levels
- **TV Series support**: Seasons and episodes with individual tracking
- **Watch history**: Track viewing progress and completion
- **User ratings and reviews**: Rate videos out of 5 stars

### Location-Based Delivery System
- **County-based organization**: All 47 Kenyan counties supported
- **Multiple delivery stations**: Each county has multiple delivery points
- **Station-specific delivery fees**: Each station can have different delivery charges
- **Example**: Mombasa County has 6 delivery stations, each with its own fee
- **International shipping**: Zone-based shipping for international customers

### Payment Integration
- **M-Pesa integration**: Local Kenyan mobile payments
- **PayPal integration**: For international customers
- **Multiple payment types**: Products, videos (rental/purchase), subscriptions
- **Payment tracking**: Complete transaction history with gateway responses

### Order Management
- **Comprehensive order tracking**: From pending to delivered
- **Order status history**: Track every status change with timestamps
- **Delivery tracking**: Tracking numbers and estimated delivery dates
- **Digital orders**: Special handling for video purchases (no physical delivery)

## 📁 Model Structure

### User & Authentication
```python
- User (Extended Django user with phone, location, profile)
```

### Location & Delivery
```python
- County (47 Kenyan counties)
- DeliveryStation (Multiple stations per county with individual fees)
- InternationalShippingZone (Zones for international shipping)
```

### Products
```python
- Category (Hierarchical categories with subcategories)
- Brand (Product brands)
- Product (Main product model)
- ProductImage (Multiple images per product)
- Size (Sizes for clothing/footwear/accessories)
- Color (Colors with hex codes)
- ProductVariant (Size+Color combinations with unique prices and stock)
```

### Videos
```python
- VideoGenre (Action, Drama, Comedy, etc.)
- Video (Movies, Series, Documentaries, etc.)
- VideoSeason (Seasons for TV series)
- VideoEpisode (Individual episodes)
- VideoSubscriptionPlan (Monthly/yearly subscription options)
- VideoPurchase (Track rentals and purchases)
- VideoWatchLater (User's watch later list)
- VideoWatchHistory (Viewing history with progress)
- UserSubscription (Active subscriptions)
- VideoRating (User ratings and reviews)
```

### Shopping & Orders
```python
- Cart (Shopping cart for products)
- CartItem (Items in cart)
- Wishlist (User's wishlist)
- Order (Main order model for products and videos)
- OrderItem (Products in an order)
- OrderStatusHistory (Track status changes)
```

### Payments
```python
- Payment (M-Pesa, PayPal, Card payments)
```

### Marketing & Engagement
```python
- ProductReview (Customer reviews with images)
- ReviewImage (Review photos)
- Coupon (Discount codes)
- CouponUsage (Track coupon redemptions)
- Notification (User notifications)
- Banner (Homepage promotional banners)
- Newsletter (Email subscriptions)
```

## 🎯 Key Business Logic

### 1. Product Variants with Size/Color Pricing
Each product can have multiple variants based on size and color:

```python
# Example: Nike T-Shirt
Product: Nike Athletic Tee
├── Variant 1: Size S, Color Red → KES 1,200
├── Variant 2: Size M, Color Red → KES 1,400
├── Variant 3: Size L, Color Red → KES 1,600
├── Variant 4: Size S, Color Blue → KES 1,200
└── Variant 5: Size M, Color Blue → KES 1,400

# Example: Adidas Shoes
Product: Adidas Running Shoes
├── Variant 1: Size 40, Color Black → KES 8,500
├── Variant 2: Size 41, Color Black → KES 8,700
├── Variant 3: Size 42, Color Black → KES 8,900
└── Variant 4: Size 43, Color White → KES 9,000
```

### 2. Video Access Control
Users can access videos through three methods:

1. **Rental** (One-time viewing)
   - User pays rental price (e.g., KES 150)
   - Can watch once
   - Access expires after watching or after 48 hours

2. **Purchase** (Unlimited viewing)
   - User pays purchase price (e.g., KES 500)
   - Unlimited views forever

3. **Subscription** (Netflix-style)
   - Monthly or yearly plan
   - Access to all subscribed content
   - Auto-renewal option

```python
# Example: User wants to watch "The Lion King"
Option 1: Rent for KES 150 → Watch once
Option 2: Buy for KES 500 → Watch unlimited
Option 3: Subscribe to Kids Plan (KES 800/month) → Watch this + all kids content
```

### 3. County-Based Delivery
Each county has multiple delivery stations with different fees:

```python
# Example: Mombasa County
DeliveryStation:
├── Mombasa Island Station → KES 150 delivery fee
├── Likoni Station → KES 200 delivery fee
├── Changamwe Station → KES 180 delivery fee
├── Jomvu Station → KES 220 delivery fee
├── Kisauni Station → KES 250 delivery fee
└── Nyali Station → KES 170 delivery fee

# Example: Nairobi County
DeliveryStation:
├── CBD Station → KES 100 delivery fee
├── Westlands Station → KES 150 delivery fee
├── Kasarani Station → KES 180 delivery fee
└── Embakasi Station → KES 200 delivery fee
```

### 4. International Shipping Zones

```python
# Example Zones
Zone 1: East Africa (Uganda, Tanzania, Rwanda) → $15 shipping, 3-5 days
Zone 2: Rest of Africa → $25 shipping, 5-10 days
Zone 3: Europe → $35 shipping, 7-14 days
Zone 4: North America → $40 shipping, 10-14 days
Zone 5: Asia → $38 shipping, 7-14 days
```

## 🛠️ Installation & Setup

### 1. Add to Django Project

```bash
# Copy models.py to your Django app
cp models.py your_app/models.py

# Copy admin.py to your Django app
cp admin.py your_app/admin.py
```

### 2. Update Settings

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'your_app',  # Your app with the models
]

# Custom User Model
AUTH_USER_MODEL = 'your_app.User'

# Media Files (for images and videos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# For international users
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'
```

### 3. Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Populate Initial Data

```python
# management/commands/populate_initial_data.py

from django.core.management.base import BaseCommand
from your_app.models import County, Size, Color

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Add all 47 Kenyan counties
        counties = [
            ('Mombasa', '001'), ('Kwale', '002'), ('Kilifi', '003'),
            ('Tana River', '004'), ('Lamu', '005'), ('Taita-Taveta', '006'),
            ('Garissa', '007'), ('Wajir', '008'), ('Mandera', '009'),
            ('Marsabit', '010'), ('Isiolo', '011'), ('Meru', '012'),
            ('Tharaka-Nithi', '013'), ('Embu', '014'), ('Kitui', '015'),
            ('Machakos', '016'), ('Makueni', '017'), ('Nyandarua', '018'),
            ('Nyeri', '019'), ('Kirinyaga', '020'), ('Murang\'a', '021'),
            ('Kiambu', '022'), ('Turkana', '023'), ('West Pokot', '024'),
            ('Samburu', '025'), ('Trans Nzoia', '026'), ('Uasin Gishu', '027'),
            ('Elgeyo-Marakwet', '028'), ('Nandi', '029'), ('Baringo', '030'),
            ('Laikipia', '031'), ('Nakuru', '032'), ('Narok', '033'),
            ('Kajiado', '034'), ('Kericho', '035'), ('Bomet', '036'),
            ('Kakamega', '037'), ('Vihiga', '038'), ('Bungoma', '039'),
            ('Busia', '040'), ('Siaya', '041'), ('Kisumu', '042'),
            ('Homa Bay', '043'), ('Migori', '044'), ('Kisii', '045'),
            ('Nyamira', '046'), ('Nairobi', '047')
        ]
        
        for name, code in counties:
            County.objects.get_or_create(name=name, code=code)
        
        # Add clothing sizes
        clothing_sizes = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL']
        for idx, size in enumerate(clothing_sizes):
            Size.objects.get_or_create(
                name=size,
                category='clothing',
                defaults={'order': idx}
            )
        
        # Add shoe sizes
        shoe_sizes = ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46']
        for idx, size in enumerate(shoe_sizes):
            Size.objects.get_or_create(
                name=size,
                category='footwear',
                defaults={'order': idx}
            )
        
        # Add basic colors
        colors = [
            ('Black', '#000000'),
            ('White', '#FFFFFF'),
            ('Red', '#FF0000'),
            ('Blue', '#0000FF'),
            ('Green', '#008000'),
            ('Yellow', '#FFFF00'),
            ('Navy', '#000080'),
            ('Gray', '#808080'),
            ('Pink', '#FFC0CB'),
            ('Brown', '#8B4513'),
        ]
        
        for name, hex_code in colors:
            Color.objects.get_or_create(name=name, defaults={'hex_code': hex_code})
        
        self.stdout.write(self.style.SUCCESS('Successfully populated initial data'))
```

Run the command:
```bash
python manage.py populate_initial_data
```

## 📊 Database Indexes

The models include strategic indexes for performance:

```python
# Product queries
indexes = [
    models.Index(fields=['slug']),
    models.Index(fields=['sku']),
    models.Index(fields=['category', 'is_active']),
]

# Video queries
indexes = [
    models.Index(fields=['slug']),
    models.Index(fields=['content_type', 'is_active']),
    models.Index(fields=['-published_at']),
]

# Order queries
indexes = [
    models.Index(fields=['order_number']),
    models.Index(fields=['user', '-created_at']),
    models.Index(fields=['status']),
]
```

## 🔐 Important Implementation Notes

### 1. Video Access Logic

```python
# In your views.py
def can_user_watch_video(user, video):
    """Check if user can watch this video"""
    
    # Free videos
    if video.is_free:
        return True
    
    # Check active subscription
    if video.requires_subscription:
        has_subscription = UserSubscription.objects.filter(
            user=user,
            status='active',
            end_date__gte=timezone.now()
        ).exists()
        if has_subscription:
            return True
    
    # Check purchase/rental
    purchase = VideoPurchase.objects.filter(
        user=user,
        video=video
    ).first()
    
    if purchase and purchase.is_accessible:
        return True
    
    return False
```

### 2. One-Time Viewing Logic

```python
# In your video player view
def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    purchase = VideoPurchase.objects.get(user=request.user, video=video)
    
    if purchase.purchase_type == 'rental':
        # First watch
        if not purchase.has_watched:
            purchase.has_watched = True
            purchase.first_watched_at = timezone.now()
            purchase.expires_at = timezone.now() + timedelta(hours=48)
        
        purchase.watch_count += 1
        purchase.save()
        
        # Check if they can still watch
        if not purchase.is_accessible:
            return redirect('rental_expired')
    
    # Continue to video player...
```

### 3. Delivery Fee Calculation

```python
def calculate_delivery_fee(user, cart):
    """Calculate delivery fee based on user location"""
    
    if user.is_international:
        # Get international zone
        country = user.get_country()  # Implement this
        zone = InternationalShippingZone.objects.filter(
            countries__icontains=country,
            is_active=True
        ).first()
        return zone.shipping_cost if zone else Decimal('50.00')
    
    else:
        # Get local delivery station
        station = user.selected_delivery_station  # User selects during checkout
        return station.delivery_fee
```

### 4. Stock Management

```python
def check_stock_and_reserve(cart_items):
    """Check stock availability and reserve items"""
    
    for item in cart_items:
        variant = item.product_variant
        
        if variant.stock_quantity < item.quantity:
            raise InsufficientStockError(
                f"Only {variant.stock_quantity} units available for {variant}"
            )
        
        # Reserve stock (reduce quantity)
        variant.stock_quantity -= item.quantity
        variant.save()
```

## 🎨 Frontend Integration Examples

### Product Listing with Variants

```django
<!-- templates/product_detail.html -->
<div class="product-detail">
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    
    <!-- Size Selection -->
    <div class="size-selector">
        <label>Select Size:</label>
        {% for variant in product.variants.filter(is_active=True).distinct.values('size') %}
            <button data-size="{{ variant.size.id }}">{{ variant.size.name }}</button>
        {% endfor %}
    </div>
    
    <!-- Color Selection -->
    <div class="color-selector">
        <label>Select Color:</label>
        {% for variant in product.variants.filter(is_active=True).distinct.values('color') %}
            <button 
                data-color="{{ variant.color.id }}"
                style="background-color: {{ variant.color.hex_code }};">
            </button>
        {% endfor %}
    </div>
    
    <!-- Price Display (updates based on selection) -->
    <div class="price">
        <span id="current-price">KES {{ selected_variant.price }}</span>
        {% if selected_variant.compare_at_price %}
            <span class="original-price">KES {{ selected_variant.compare_at_price }}</span>
        {% endif %}
    </div>
    
    <!-- Stock Status -->
    <div class="stock-status">
        {% if selected_variant.is_in_stock %}
            <span class="in-stock">In Stock ({{ selected_variant.stock_quantity }} available)</span>
        {% else %}
            <span class="out-of-stock">Out of Stock</span>
        {% endif %}
    </div>
    
    <button id="add-to-cart">Add to Cart</button>
</div>
```

### Video Player with Access Control

```django
<!-- templates/video_player.html -->
{% if can_watch %}
    <div class="video-player">
        <video id="video-player" controls>
            <source src="{{ video.video_url }}" type="video/mp4">
        </video>
        
        {% if purchase.purchase_type == 'rental' %}
            <div class="rental-notice">
                <p>Rental: You have {{ purchase.watch_count }} view{{ purchase.watch_count|pluralize }} remaining</p>
                <p>Expires: {{ purchase.expires_at }}</p>
            </div>
        {% endif %}
    </div>
{% else %}
    <div class="purchase-options">
        <h2>{{ video.title }}</h2>
        <img src="{{ video.poster.url }}" alt="{{ video.title }}">
        
        <div class="pricing">
            <div class="option">
                <h3>Rent</h3>
                <p>KES {{ video.rental_price }}</p>
                <p>Watch once</p>
                <button class="btn-rent">Rent Now</button>
            </div>
            
            {% if video.purchase_price %}
            <div class="option">
                <h3>Buy</h3>
                <p>KES {{ video.purchase_price }}</p>
                <p>Watch unlimited</p>
                <button class="btn-buy">Buy Now</button>
            </div>
            {% endif %}
            
            <div class="option">
                <h3>Subscribe</h3>
                <p>From KES 800/month</p>
                <p>Watch this + more</p>
                <button class="btn-subscribe">See Plans</button>
            </div>
        </div>
    </div>
{% endif %}
```

### Delivery Station Selection

```django
<!-- templates/checkout.html -->
<form method="post">
    {% csrf_token %}
    
    <!-- Product items -->
    
    <!-- Delivery Selection -->
    <div class="delivery-section">
        {% if not user.is_international %}
            <h3>Select Delivery Station</h3>
            <select name="delivery_station" required>
                {% for county in counties %}
                    <optgroup label="{{ county.name }}">
                        {% for station in county.delivery_stations.filter(is_active=True) %}
                            <option value="{{ station.id }}">
                                {{ station.name }} - KES {{ station.delivery_fee }}
                            </option>
                        {% endfor %}
                    </optgroup>
                {% endfor %}
            </select>
        {% else %}
            <h3>International Shipping</h3>
            <select name="shipping_zone" required>
                {% for zone in shipping_zones %}
                    <option value="{{ zone.id }}">
                        {{ zone.name }} - ${{ zone.shipping_cost }} 
                        ({{ zone.estimated_delivery_days }} days)
                    </option>
                {% endfor %}
            </select>
        {% endif %}
    </div>
    
    <!-- Order Summary -->
    <div class="order-summary">
        <p>Subtotal: KES {{ cart.subtotal }}</p>
        <p>Delivery: <span id="delivery-fee">-</span></p>
        <p><strong>Total: <span id="total">-</span></strong></p>
    </div>
    
    <!-- Payment Method -->
    <div class="payment-method">
        <label>
            <input type="radio" name="payment_method" value="mpesa" required>
            M-Pesa
        </label>
        <label>
            <input type="radio" name="payment_method" value="paypal" required>
            PayPal
        </label>
    </div>
    
    <button type="submit">Place Order</button>
</form>
```

## 🔌 Payment Gateway Integration

### M-Pesa STK Push Example

```python
# payments/mpesa.py

import requests
from django.conf import settings

def initiate_mpesa_payment(phone_number, amount, order_id):
    """Initiate M-Pesa STK Push"""
    
    # Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    access_token = response.json()['access_token']
    
    # STK Push request
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": settings.MPESA_PASSWORD,
        "Timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"Order-{order_id}",
        "TransactionDesc": f"Payment for Order {order_id}"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Callback handler
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    
    data = request.body
    callback_data = data.get('Body', {}).get('stkCallback', {})
    
    if callback_data.get('ResultCode') == 0:
        # Payment successful
        checkout_request_id = callback_data.get('CheckoutRequestID')
        
        # Update payment record
        payment = Payment.objects.get(transaction_id=checkout_request_id)
        payment.status = 'completed'
        payment.mpesa_receipt = callback_data['CallbackMetadata']['Item'][1]['Value']
        payment.paid_at = timezone.now()
        payment.save()
        
        # Update order
        payment.order.status = 'confirmed'
        payment.order.save()
    
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
```

## 📱 API Endpoints (Django REST Framework)

```python
# urls.py

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'cart', views.CartViewSet)

urlpatterns = router.urls

# Example ViewSet
from rest_framework import viewsets
from .models import Product, ProductVariant
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by brand
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            queryset = queryset.filter(base_price__gte=min_price, base_price__lte=max_price)
        
        return queryset
```

## 🔍 Search & Filtering

```python
# Add django-filter for advanced filtering

from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="base_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="base_price", lookup_expr='lte')
    category = filters.CharFilter(field_name="category__slug")
    brand = filters.CharFilter(field_name="brand__slug")
    
    class Meta:
        model = Product
        fields = ['category', 'brand', 'product_type', 'is_featured']

class VideoFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name="genres__slug")
    min_year = filters.NumberFilter(field_name="release_year", lookup_expr='gte')
    max_year = filters.NumberFilter(field_name="release_year", lookup_expr='lte')
    
    class Meta:
        model = Video
        fields = ['content_type', 'rating', 'is_free', 'requires_subscription']
```

## 📈 Analytics Queries

```python
# Common analytics queries

# Top selling products
from django.db.models import Count, Sum

top_products = Product.objects.annotate(
    total_sold=Sum('variants__orderitem__quantity')
).order_by('-total_sold')[:10]

# Most watched videos
top_videos = Video.objects.annotate(
    purchase_count=Count('purchases')
).order_by('-purchase_count')[:10]

# Revenue by category
from django.db.models import F

category_revenue = Category.objects.annotate(
    revenue=Sum(F('products__variants__orderitem__total_price'))
).order_by('-revenue')

# County delivery statistics
county_orders = County.objects.annotate(
    order_count=Count('delivery_stations__orders')
).order_by('-order_count')
```

## 🧪 Testing Examples

```python
# tests/test_models.py

from django.test import TestCase
from decimal import Decimal
from your_app.models import Product, ProductVariant, Size, Color

class ProductVariantTestCase(TestCase):
    def setUp(self):
        self.size_s = Size.objects.create(name='S', category='clothing')
        self.size_m = Size.objects.create(name='M', category='clothing')
        self.color_red = Color.objects.create(name='Red', hex_code='#FF0000')
        self.color_blue = Color.objects.create(name='Blue', hex_code='#0000FF')
        
        self.product = Product.objects.create(
            name='Test T-Shirt',
            sku='TEST-001',
            product_type='clothing',
            base_price=Decimal('1000.00')
        )
    
    def test_variant_pricing(self):
        """Test that each size/color combo has unique pricing"""
        variant_s_red = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001-S-RED',
            size=self.size_s,
            color=self.color_red,
            price=Decimal('1000.00'),
            stock_quantity=50
        )
        
        variant_m_red = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001-M-RED',
            size=self.size_m,
            color=self.color_red,
            price=Decimal('1200.00'),
            stock_quantity=30
        )
        
        self.assertEqual(variant_s_red.price, Decimal('1000.00'))
        self.assertEqual(variant_m_red.price, Decimal('1200.00'))
        self.assertNotEqual(variant_s_red.price, variant_m_red.price)
    
    def test_stock_tracking(self):
        """Test stock quantity tracking"""
        variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001-S-BLUE',
            size=self.size_s,
            color=self.color_blue,
            price=Decimal('1000.00'),
            stock_quantity=10,
            low_stock_threshold=5
        )
        
        self.assertFalse(variant.is_low_stock)
        
        variant.stock_quantity = 4
        variant.save()
        
        self.assertTrue(variant.is_low_stock)
```

## 🚀 Performance Optimization

### 1. Use select_related and prefetch_related

```python
# Optimize product queries
products = Product.objects.select_related(
    'category', 'brand'
).prefetch_related(
    'images', 'variants__size', 'variants__color'
).filter(is_active=True)

# Optimize order queries
orders = Order.objects.select_related(
    'user', 'delivery_station__county'
).prefetch_related(
    'items__product_variant__product'
).filter(user=request.user)
```

### 2. Database Indexes

Already included in the models for optimal query performance.

### 3. Caching

```python
from django.core.cache import cache

def get_featured_products():
    """Cache featured products for 1 hour"""
    cache_key = 'featured_products'
    products = cache.get(cache_key)
    
    if not products:
        products = Product.objects.filter(
            is_featured=True,
            is_active=True
        ).select_related('category', 'brand')[:10]
        cache.set(cache_key, products, 3600)  # 1 hour
    
    return products
```

## 📝 Final Notes

### Security Considerations
1. Always validate payment callbacks
2. Use HTTPS for all payment transactions
3. Implement rate limiting on API endpoints
4. Sanitize user inputs
5. Use Django's CSRF protection
6. Secure media file access (especially for paid videos)

### Scalability
1. Use CDN for images and videos
2. Implement caching strategy
3. Use task queues (Celery) for heavy operations
4. Consider database read replicas for heavy traffic
5. Optimize video streaming (HLS, DASH)

### Compliance
1. GDPR compliance for user data
2. Payment gateway PCI-DSS compliance
3. Copyright protection for videos
4. Age verification for restricted content
5. Terms of service and privacy policy

## 🤝 Support

For questions or support, contact the development team.

---

**Built for Mukurugenzi E-commerce Platform**
**Version 1.0**
**Django 4.2+**