from django.shortcuts import render


def home(request):
    return render(request, "store_app/home.html")


def about(request):
    return render(request, "store_app/about.html")

def wishlist(request):
    return render(request, 'store_app/wishlist.html')