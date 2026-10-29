from django.urls import path
from . import views

app_name = "payment_app"

urlpatterns = [
    path("", views.payment_page, name="payment_page"),
]
