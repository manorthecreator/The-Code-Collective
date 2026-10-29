from django.urls import path
from . import views

app_name = "orders_app"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("checkout/place-order/", views.place_order, name="place_order"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
]
