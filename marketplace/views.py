import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch, Q
from .models import *
from .forms import ReviewForm, OrderForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


# Update your home view like this
def home(request):
    if request.method == 'POST':
        # This block handles the contact form submission
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message_body = request.POST.get('message')

        if first_name and last_name and email and message_body:
            full_name = f"{first_name} {last_name}"
            
            subject = f"New Contact Form Submission from {full_name}"
            email_message = f"""
            You have received a new message from your website contact form.

            Name: {full_name}
            Email: {email}

            Message:
            {message_body}
            """
            
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL, # The sender's email
                    [settings.CONTACT_EMAIL],    # The recipient list
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message! We will get back to you shortly.')
            except Exception as e:
                messages.error(request, f'Sorry, there was an error sending your message. Please try again later. Error: {e}')
            
            return redirect('marketplace:home' + '#Contact')

    # This part handles the GET request to display the page
    products = Product.objects.filter(display=True).prefetch_related('images')[:4]
    context = {
        'products': products,
    }
    return render(request, 'index.html', context)

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal('0.00')
    if cart:
        # Extract product IDs from the cart item keys
        product_ids = [item['product_id'] for item in cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}
        
        for cart_key, item_data in cart.items():
            product = product_map.get(item_data['product_id'])
            if product:
                quantity = item_data['quantity']
                subtotal = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'size': item_data.get('size'),
                    'subtotal': subtotal,
                    'cart_key': cart_key, # Pass key for removal
                })
                total_price += subtotal
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect('marketplace:shop')

    # This logic is now common for GET and POST, so let's compute it once.
    cart_items_for_display = []
    total_price = Decimal('0.00')
    line_items_for_stripe = []
    
    if cart:
        product_ids = [item['product_id'] for item in cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for cart_key, item_data in cart.items():
            product = product_map.get(item_data['product_id'])
            if product:
                quantity = item_data['quantity']
                subtotal = product.price * quantity
                total_price += subtotal
                
                cart_items_for_display.append({
                    'product': product, 
                    'quantity': quantity, 
                    'subtotal': subtotal
                })
                
                # Build a descriptive name for Stripe
                product_name_parts = [product.name]
                variant_parts = []
                if item_data.get('size'):
                    variant_parts.append(item_data.get('size'))
                if variant_parts:
                    product_name_parts.append(f"({', '.join(variant_parts)})")

                line_items_for_stripe.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': ' '.join(product_name_parts)},
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': quantity,
                })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer_email = form.cleaned_data.get('email')

            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items_for_stripe,
                    mode='payment',
                    customer_email=customer_email,
                    success_url=request.build_absolute_uri(reverse('marketplace:stripe_success')),
                    cancel_url=request.build_absolute_uri(reverse('marketplace:stripe_cancel')),
                    metadata={
                        'user_id': request.user.id,
                        'cart': json.dumps(cart),
                        'shipping_info': json.dumps(form.cleaned_data)
                    }
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(request, f"Something went wrong with the payment process: {e}")
                return redirect('marketplace:cart')
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items_for_display,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)

def faqs(request):
    return render(request, 'faqs.html')

def product_details(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'reviews__user', 'sizes'), 
        id=product_id, 
        is_available=True
    )

    reviews = product.reviews.all()

    related_products = []
    if product.category:
        related_products = Product.objects.filter(
            category=product.category, 
            is_available=True
        ).exclude(id=product.id).prefetch_related('images')[:4]
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a review.")
            return redirect('accounts:login')

        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('marketplace:product_details', product_id=product.id)
    else:
        review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size = request.POST.get('size')

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid quantity.")
        
        product = get_object_or_404(Product, id=product_id, is_available=True)

        if product.stock < quantity:
            messages.error(request, f"Sorry, only {product.stock} of this item are available.")
            return redirect('marketplace:product_details', product_id=product.id)

        cart = request.session.get('cart', {})
        
        # Create a unique key for the cart item based on product and its variants
        size_key = size or 'none'
        cart_item_key = f"{product.id}-{size_key}"

        if cart_item_key in cart:
            cart[cart_item_key]['quantity'] += quantity
        else:
            cart[cart_item_key] = {
                'product_id': product.id,
                'quantity': quantity,
                'size': size,
            }
        
        request.session['cart'] = cart
        messages.success(request, f"'{product.name}' has been added to your cart.")
        return redirect('marketplace:cart')

    return redirect('marketplace:shop')

@login_required
def remove_from_cart(request, cart_item_key):
    cart = request.session.get('cart', {})
    if cart_item_key in cart:
        del cart[cart_item_key]
        request.session['cart'] = cart
        messages.success(request, "Item removed from your cart.")
    return redirect('marketplace:cart')

@login_required
def order_confirmation(request):
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    if not order:
        messages.error(request, "No recent order found.")
        return redirect('marketplace:shop')
    context = {
        'order': order
    }
    return render(request, 'order.html', context)

def privacy(request):
    return render(request, 'privacy.html')

def shop(request):
    categories = Category.objects.all()
    product_list = Product.objects.filter(is_available=True).prefetch_related('images').order_by('-created_at')
    
    selected_category_name = request.GET.get('category')

    if selected_category_name:
        # Using __name__iexact for case-insensitive matching
        product_list = product_list.filter(category__name__iexact=selected_category_name)

    paginator = Paginator(product_list, 8) # Show 8 products per page

    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category_name,
    }
    return render(request, 'shop.html', context)

def terms(request):
    return render(request, 'terms.html')

@login_required
def stripe_success(request):
    # The order is created by the webhook. We clear the cart from the session here.
    request.session['cart'] = {}
    messages.success(request, "Your payment was successful! Your order is being processed.")
    # Redirect to a user's order history page or home. The order confirmation page 
    # requires an order_id, which we don't have here as it's created by the webhook.
    return redirect('marketplace:order_confirmation')

@login_required
def stripe_cancel(request):
    messages.error(request, "Your payment was cancelled. You have not been charged.")
    return redirect('marketplace:cart')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve metadata
        user_id = session.get('metadata', {}).get('user_id')
        cart_json = session.get('metadata', {}).get('cart')
        shipping_info_json = session.get('metadata', {}).get('shipping_info')
        payment_intent_id = session.get('payment_intent')

        if not all([user_id, cart_json, shipping_info_json]):
            return HttpResponse("Webhook Error: Missing metadata", status=400)
            
        try:
            user = User.objects.get(id=user_id)
            cart = json.loads(cart_json)
            shipping_info = json.loads(shipping_info_json)
            # Call the order creation logic
            create_order_from_webhook(user, cart, shipping_info, payment_intent_id)

        except User.DoesNotExist:
            return HttpResponse(f"Webhook Error: User with id {user_id} not found.", status=404)
        except Exception as e:
            # Log the error and notify admin
            print(f"Error processing webhook: {e}")
            return HttpResponse(f"Webhook Error: {e}", status=500)

    return HttpResponse(status=200)

def create_order_from_webhook(user, cart, shipping_info, payment_intent_id):
    """
    Creates an order and its items from the cart data provided by the webhook.
    This runs inside a transaction to ensure atomicity.
    """
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            status=Order.OrderStatus.PROCESSING,
            stripe_payment_intent_id=payment_intent_id,
            **shipping_info
        )
        
        product_ids = [item['product_id'] for item in cart.values()]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        products_map = {p.id: p for p in products}

        for cart_key, item_data in cart.items():
            product_id = item_data.get('product_id')
            product = products_map.get(product_id)
            quantity = item_data.get('quantity')
            
            if not product or product.stock < quantity:
                raise Exception(f"Product {product.name if product else product_id} is out of stock.")
            
            order_item_data = {
                'quantity': item_data.get('quantity'),
                'size': item_data.get('size'),
            }

            OrderItem.objects.create(
                order=order, product=product, price=product.price, **order_item_data
            )
            product.stock -= quantity
            product.save(update_fields=['stock'])