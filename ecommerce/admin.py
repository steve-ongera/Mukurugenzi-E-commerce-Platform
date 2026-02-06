"""
Mukurugenzi E-commerce Platform - Django Admin Configuration
Professional admin interface for managing products, videos, orders, and more
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import *


# ============================================================================
# USER ADMIN
# ============================================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_international', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_international', 'date_joined']
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'address', 'profile_image')
        }),
        ('Location', {
            'fields': ('is_international',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )


# ============================================================================
# LOCATION & DELIVERY ADMIN
# ============================================================================

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'slug', 'station_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def station_count(self, obj):
        return obj.delivery_stations.count()
    station_count.short_description = 'Delivery Stations'


@admin.register(DeliveryStation)
class DeliveryStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'delivery_fee', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'county', 'created_at']
    search_fields = ['name', 'address', 'phone_number', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'county', 'address')
        }),
        ('Contact', {
            'fields': ('phone_number', 'email')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('delivery_fee',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(InternationalShippingZone)
class InternationalShippingZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'shipping_cost', 'estimated_delivery_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'countries']
    prepopulated_fields = {'slug': ('name',)}


# ============================================================================
# PRODUCT CATEGORY & BRAND ADMIN
# ============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'category_image']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Media', {
            'fields': ('image', 'category_image')
        }),
        ('Display', {
            'fields': ('order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

    def category_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "No image"
    category_image.short_description = 'Preview'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'brand_logo']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

    def brand_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="200" />', obj.logo.url)
        return "No logo"
    brand_logo.short_description = 'Logo Preview'


# ============================================================================
# PRODUCT ADMIN
# ============================================================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['sku', 'size', 'color', 'price', 'stock_quantity', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'product_type', 'category', 'brand', 'base_price', 
                   'variant_count', 'is_active', 'is_featured', 'created_at']
    list_filter = ['product_type', 'category', 'brand', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'product_type', 'category', 'brand')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'material', 'care_instructions')
        }),
        ('Pricing', {
            'fields': ('base_price', 'compare_at_price')
        }),
        ('Inventory', {
            'fields': ('track_inventory',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Variants'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'order', 'image_preview', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


# ============================================================================
# PRODUCT ATTRIBUTES ADMIN
# ============================================================================

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'hex_code']

    def color_preview(self, obj):
        return format_html(
            '<div style="width:50px; height:20px; background-color:{}; border:1px solid #ccc;"></div>',
            obj.hex_code
        )
    color_preview.short_description = 'Color'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'size', 'color', 'price', 'stock_quantity', 
                   'stock_status', 'is_active', 'created_at']
    list_filter = ['is_active', 'size', 'color', 'created_at']
    search_fields = ['sku', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'variant_image_preview']

    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            color = 'red'
            text = 'Out of Stock'
        elif obj.is_low_stock:
            color = 'orange'
            text = 'Low Stock'
        else:
            color = 'green'
            text = 'In Stock'
        return format_html('<span style="color: {};">{}</span>', color, text)
    stock_status.short_description = 'Stock Status'

    def variant_image_preview(self, obj):
        if obj.variant_image:
            return format_html('<img src="{}" width="200" />', obj.variant_image.url)
        return "No image"
    variant_image_preview.short_description = 'Image Preview'


# ============================================================================
# VIDEO ADMIN
# ============================================================================

@admin.register(VideoGenre)
class VideoGenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'video_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Videos'


class VideoSeasonInline(admin.TabularInline):
    model = VideoSeason
    extra = 0
    fields = ['season_number', 'title', 'release_year']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'release_year', 'duration_minutes', 'rental_price', 
                   'views_count', 'average_rating', 'is_active', 'is_featured', 'published_at']
    list_filter = ['content_type', 'is_active', 'is_featured', 'is_free', 'requires_subscription', 
                  'rating', 'release_year', 'created_at']
    search_fields = ['title', 'description', 'cast', 'director']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'average_rating', 'created_at', 'updated_at', 
                      'thumbnail_preview', 'poster_preview']
    filter_horizontal = ['genres']
    inlines = [VideoSeasonInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content_type', 'genres')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Credits', {
            'fields': ('director', 'cast', 'release_year', 'rating')
        }),
        ('Media Details', {
            'fields': ('duration_minutes', 'language', 'subtitles_available')
        }),
        ('Media Files', {
            'fields': ('thumbnail', 'thumbnail_preview', 'poster', 'poster_preview', 
                      'trailer_url', 'video_file', 'video_url')
        }),
        ('Pricing & Access', {
            'fields': ('rental_price', 'purchase_price', 'is_free', 'requires_subscription')
        }),
        ('Statistics', {
            'fields': ('views_count', 'average_rating')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="200" />', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = 'Thumbnail Preview'

    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="200" />', obj.poster.url)
        return "No poster"
    poster_preview.short_description = 'Poster Preview'


class VideoEpisodeInline(admin.TabularInline):
    model = VideoEpisode
    extra = 1
    fields = ['episode_number', 'title', 'duration_minutes', 'air_date', 'is_active']


@admin.register(VideoSeason)
class VideoSeasonAdmin(admin.ModelAdmin):
    list_display = ['video', 'season_number', 'title', 'release_year', 'episode_count', 'created_at']
    list_filter = ['release_year', 'created_at']
    search_fields = ['video__title', 'title']
    inlines = [VideoEpisodeInline]

    def episode_count(self, obj):
        return obj.episodes.count()
    episode_count.short_description = 'Episodes'


@admin.register(VideoEpisode)
class VideoEpisodeAdmin(admin.ModelAdmin):
    list_display = ['season', 'episode_number', 'title', 'duration_minutes', 'air_date', 'is_active']
    list_filter = ['is_active', 'air_date', 'created_at']
    search_fields = ['title', 'description', 'season__video__title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'thumbnail_preview']

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="200" />', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = 'Thumbnail Preview'


@admin.register(VideoSubscriptionPlan)
class VideoSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'yearly_price', 'max_simultaneous_streams', 
                   'video_quality', 'is_active', 'is_featured', 'order']
    list_filter = ['is_active', 'is_featured', 'download_allowed']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['genres_access']


# ============================================================================
# VIDEO PURCHASE & ACCESS ADMIN
# ============================================================================

@admin.register(VideoPurchase)
class VideoPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'purchase_type', 'price_paid', 'watch_count', 
                   'access_status', 'purchased_at']
    list_filter = ['purchase_type', 'has_watched', 'purchased_at']
    search_fields = ['user__username', 'user__email', 'video__title']
    readonly_fields = ['purchased_at']

    def content(self, obj):
        if obj.video:
            return obj.video.title
        return str(obj.episode)
    content.short_description = 'Content'

    def access_status(self, obj):
        if obj.is_accessible:
            return format_html('<span style="color: green;">✓ Accessible</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')
    access_status.short_description = 'Access'


@admin.register(VideoWatchLater)
class VideoWatchLaterAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'video__title']

    def content(self, obj):
        if obj.video:
            return obj.video.title
        return str(obj.episode)
    content.short_description = 'Content'


@admin.register(VideoWatchHistory)
class VideoWatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'progress_percentage', 'completed', 'watched_at']
    list_filter = ['completed', 'watched_at']
    search_fields = ['user__username', 'video__title']

    def content(self, obj):
        if obj.video:
            return obj.video.title
        return str(obj.episode)
    content.short_description = 'Content'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'created_at']
    list_filter = ['status', 'auto_renew', 'plan', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VideoRating)
class VideoRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__username', 'video__title', 'review']
    readonly_fields = ['created_at', 'updated_at']


# ============================================================================
# CART & WISHLIST ADMIN
# ============================================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_owner', 'total_items', 'subtotal', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'subtotal']
    inlines = [CartItemInline]

    def cart_owner(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest ({obj.session_key[:8]}...)"
    cart_owner.short_description = 'Owner'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']


# ============================================================================
# ORDER ADMIN
# ============================================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'delivery_type', 
                   'created_at', 'updated_at']
    list_filter = ['status', 'delivery_type', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'tracking_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'delivery_type')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'total_amount')
        }),
        ('Delivery Information', {
            'fields': ('delivery_station', 'shipping_zone', 'shipping_address', 'shipping_phone')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'estimated_delivery', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']


# ============================================================================
# PAYMENT ADMIN
# ============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_method', 'amount', 'currency', 
                   'status', 'transaction_type', 'paid_at', 'created_at']
    list_filter = ['payment_method', 'status', 'currency', 'created_at']
    search_fields = ['payment_id', 'user__username', 'transaction_id', 'mpesa_receipt', 
                    'paypal_transaction_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'user', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('order', 'video_purchase', 'subscription')
        }),
        ('Gateway Details', {
            'fields': ('transaction_id', 'mpesa_receipt', 'mpesa_phone', 'paypal_transaction_id')
        }),
        ('Response Data', {
            'fields': ('gateway_response', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'created_at', 'updated_at')
        }),
    )

    def transaction_type(self, obj):
        if obj.order:
            return "Product Order"
        elif obj.video_purchase:
            return "Video Purchase"
        elif obj.subscription:
            return "Subscription"
        return "Unknown"
    transaction_type.short_description = 'Type'


# ============================================================================
# REVIEW ADMIN
# ============================================================================

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'verified_purchase', 'is_approved', 
                   'helpful_count', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'review']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReviewImageInline]


# ============================================================================
# COUPON ADMIN
# ============================================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'times_used', 'usage_limit',
                   'valid_from', 'valid_until', 'is_active', 'validity_status']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at']
    search_fields = ['code', 'description']
    filter_horizontal = ['applicable_to_products', 'applicable_to_categories']
    readonly_fields = ['times_used', 'created_at', 'validity_status']

    def validity_status(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid/Expired</span>')
    validity_status.short_description = 'Status'


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__username', 'order__order_number']


# ============================================================================
# NOTIFICATION ADMIN
# ============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']


# ============================================================================
# SITE SETTINGS ADMIN
# ============================================================================

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'start_date', 'end_date', 'banner_preview']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'banner_preview']

    def banner_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return "No image"
    banner_preview.short_description = 'Preview'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']