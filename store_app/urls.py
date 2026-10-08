from django.urls import path
from . import views

app_name = "store_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("wishlist/", views.wishlist, name="wishlist"),
]