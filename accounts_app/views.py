from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

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


@login_required(login_url="accounts_app:login")
def account_info(request):
    user = request.user

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        new_password = request.POST.get("password", "")

        # Check whether another user already uses this email
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            messages.error(request, "This email address is already in use.")
            return redirect("accounts_app:account")

        # Update the user's information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Change password only if a new one was entered
        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

        messages.success(request, "Your account information has been updated successfully.")
        return redirect("accounts_app:account")

    return render(request, "accounts_app/account_information.html")