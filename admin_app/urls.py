from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products_view, name='products'),
    path('customers/', views.customers_view, name='customers'),
    path('orders/', views.orders_view, name='orders'),
    path('settings/', views.settings_view, name='settings'),
    path('analytics/', views.analytics_view, name='analytics'),
]