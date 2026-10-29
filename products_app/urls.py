from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path('product/<int:productID>/',views.product_detail,name='product_detail'),
]