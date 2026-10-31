from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products_app.models import Product

def home(request):
    new_arrivals = Product.objects.filter(
        status='Available'
    ).order_by('-productID')[:4]

    context = {
        'new_arrivals': new_arrivals,
    }

    return render(request, 'store_app/home.html', context)


def about(request):
    return render(request, "store_app/about.html")

@login_required(login_url='/accounts_app/login/')
def wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = request.user.wishlist_items.all()
    else:
        wishlist_items = []

    return render(request, 'store_app/wishlist.html', {
        'wishlist_items': wishlist_items
    })