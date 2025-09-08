from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('' , views.home , name='home'),
    path('cart/' , views.cart , name='cart'),
    path('checkout/' , views.checkout , name='checkout'),
    path('faqs/' , views.faqs , name='faqs'),   
    path('product/<int:product_id>/' , views.product_details , name='product_details'),
    path('cart/add/' , views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:cart_item_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/confirmation/' , views.order_confirmation , name='order_confirmation'),
    path('privacy/' , views.privacy , name='privacy'),
    path('shop/' , views.shop , name='shop'),
    path('terms/' , views.terms , name='terms'),
    # Stripe webhook endpoints
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel, name='stripe_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
