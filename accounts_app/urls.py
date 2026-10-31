from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
app_name = 'accounts_app'
urlpatterns = [
    path('',views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('account/', views.account_info, name='account'),
    path('logout/',LogoutView.as_view(next_page='accounts_app:login'),name='logout'),
]