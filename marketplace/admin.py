from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ProductImage, Review, Size
# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # How many extra forms to show
    readonly_fields = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'category', 'price', 'stock', 'is_available')
    list_filter = ('is_available', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('sizes',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ('price', 'size')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'total_price']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'stripe_payment_intent_id', 'created_at', 'updated_at', 'total_price')
    search_fields = ('id', 'user__username', 'email', 'first_name', 'last_name')

admin.site.register(Category)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.site_header = "Cashstronomy Clothing Admin"
admin.site.site_title = "Cashstronomy Clothing Admin Portal"