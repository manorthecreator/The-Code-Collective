from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products_app.models import Product
from .models import Order, OrderItem

DELIVERY_FEE = Decimal("100.00")
CART_SESSION_KEY = "velora_cart"


def _cart_context(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    rows = []
    subtotal = Decimal("0.00")
    cleaned_cart = {}

    for product_id, quantity in cart.items():
        try:
            quantity = int(quantity)
            if quantity < 1:
                continue
            product = Product.objects.get(productID=int(product_id), status="Available")
        except (ValueError, TypeError, Product.DoesNotExist):
            continue

        cleaned_cart[str(product.productID)] = quantity
        line_total = product.price * quantity
        subtotal += line_total
        rows.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    request.session[CART_SESSION_KEY] = cleaned_cart
    delivery = DELIVERY_FEE if rows else Decimal("0.00")
    return {
        "cart_items": rows,
        "subtotal": subtotal,
        "delivery_fee": delivery,
        "total": subtotal + delivery,
        "item_count": sum(row["quantity"] for row in rows),
    }


def cart_view(request):
    return render(request, "orders_app/cart.html", _cart_context(request))


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, productID=product_id, status="Available")
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (ValueError, TypeError):
        quantity = 1
    quantity = max(1, min(quantity, 99))

    cart = request.session.get(CART_SESSION_KEY, {})
    key = str(product.productID)
    cart[key] = min(int(cart.get(key, 0)) + quantity, 99)
    request.session[CART_SESSION_KEY] = cart
    messages.success(request, f"{product.name} added to your cart.")
    next_url = request.POST.get("next")
    return redirect(next_url) if next_url else redirect("orders_app:cart")


@require_POST
def update_cart(request, product_id):
    cart = request.session.get(CART_SESSION_KEY, {})
    key = str(product_id)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = min(quantity, 99)

    request.session[CART_SESSION_KEY] = cart
    return redirect("orders_app:cart")


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get(CART_SESSION_KEY, {})
    cart.pop(str(product_id), None)
    request.session[CART_SESSION_KEY] = cart
    return redirect("orders_app:cart")


def checkout_view(request):
    context = _cart_context(request)
    if not context["cart_items"]:
        messages.info(request, "Your cart is empty. Add a product before checkout.")
        return redirect("products:product_list")
    return render(request, "orders_app/payment.html", context)


@require_POST
def place_order(request):
    context = _cart_context(request)
    if not context["cart_items"]:
        messages.error(request, "Your cart is empty.")
        return redirect("orders_app:cart")

    customer_name = request.POST.get("customer_name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("delivery_address", "").strip()
    payment_method = request.POST.get("payment_method", "cash")

    if not all([customer_name, email, phone, address]):
        messages.error(request, "Please complete all delivery and contact details.")
        return redirect("orders_app:checkout")

    if payment_method not in ("cash", "card"):
        messages.error(request, "Please select a valid payment method.")
        return redirect("orders_app:checkout")

    # Do not collect/store card numbers, expiry dates or CVV. A real card
    # transaction must be handled by a payment provider's hosted checkout.
    if payment_method == "card":
        messages.error(
            request,
            "Online card payments are not connected yet. Choose cash on delivery, "
            "or connect a payment provider before enabling card payments."
        )
        return redirect("orders_app:checkout")

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            delivery_address=address,
            payment_method=payment_method,
            status="CONFIRMED",
            subtotal=context["subtotal"],
            delivery_fee=context["delivery_fee"],
            total=context["total"],
        )
        for row in context["cart_items"]:
            product = row["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=row["quantity"],
            )

    request.session[CART_SESSION_KEY] = {}
    request.session["last_order_id"] = order.pk
    return redirect("orders_app:order_success", order_id=order.pk)


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders_app/order_success.html", {"order": order})
