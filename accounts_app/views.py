import re
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

            if user.is_superuser:
                return redirect('admin_app:dashboard')
            else:
                return redirect('store_app:home')

        else:
            return render(
                request,
                'accounts_app/login.html',
                {
                    'error': 'Invalid email or password.'
                }
            )

    return render(request, 'accounts_app/login.html')



def register(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check password length
        if len(password) <= 10 or len(password) >= 16:
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Password must contain 11 to 15 characters.'
                }
            )

        # Check if the first character is uppercase
        if not re.match(r'^[A-Z]', password):
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Password must start with a capital letter.'
                }
            )

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Password must contain at least one lowercase letter.'
                }
            )

        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Password must contain at least one digit.'
                }
            )

        # Check for at least one special character
        if not re.search(r'[^A-Za-z0-9]', password):
            return render(
                request,
                'accounts_app/register.html',
                {
                    'error': 'Password must contain at least one special character.'
                }
            )

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

        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check the current password
        if not user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect("accounts_app:account")

        # Check password length
        if len(new_password) < 11 or len(new_password) > 15:
            messages.error(
                request,
                "Password must contain 11 to 15 characters."
            )
            return redirect("accounts_app:account")

        # Check that the first character is uppercase
        if not re.match(r'^[A-Z]', new_password):
            messages.error(
                request,
                "Password must start with a capital letter."
            )
            return redirect("accounts_app:account")

        # Check for a lowercase letter
        if not re.search(r'[a-z]', new_password):
            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )
            return redirect("accounts_app:account")

        # Check for a digit
        if not re.search(r'[0-9]', new_password):
            messages.error(
                request,
                "Password must contain at least one digit."
            )
            return redirect("accounts_app:account")

        # Check for a special character
        if not re.search(r'[^A-Za-z0-9]', new_password):
            messages.error(
                request,
                "Password must contain at least one special character."
            )
            return redirect("accounts_app:account")

        # Check that the new passwords match
        if new_password != confirm_password:
            messages.error(
                request,
                "The new passwords do not match."
            )
            return redirect("accounts_app:account")

        # Save the new password to the user's account
        user.set_password(new_password)
        user.save()

        # Keep the user logged in after changing the password
        update_session_auth_hash(request, user)

        messages.success(
            request,
            "Your password has been updated successfully."
        )

        return redirect("accounts_app:account")

    return render(
        request,
        "accounts_app/account_information.html"
    )
