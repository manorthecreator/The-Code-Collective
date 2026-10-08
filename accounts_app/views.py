from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
# Create your views here.

def index(request):
    #return HttpResponse("Hello from My App!")
    return render(request, 'accounts_app/login.html')

def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)

            return redirect('store_app:home')

        else:
            return render(
                request,
                'accounts_app/login.html',
                {
                    'error': 'Invalid email or password.'
                }
            )


def register(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'An account with this email already exists.'
                }
            )

        # Create the user
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Go to login page
        return redirect('accounts_app:index')

    return render(request, 'accounts_app/register.html')
