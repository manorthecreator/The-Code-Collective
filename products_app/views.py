from django.shortcuts import render,get_object_or_404
from .models import Product,Category,ProductVariant

# Create your views here.
from django.db.models import Avg
from reviews_app.forms import ReviewForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def product_list(request):
    products = Product.objects.filter(status='Available')
    categories = Category.objects.all()
    colors=(
        ProductVariant.objects
        .values('color', 'colorCode')
        .distinct()
    )
    sizes_raw = ProductVariant.objects.values_list('size', flat=True).distinct()
    size_order = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5, 'XXL': 6}
    sizes = sorted(sizes_raw, key=lambda x: size_order.get(x, 99))
    category = request.GET.get("category")
    if category and category != "all":
        products = products.filter(category_id=category)

    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')
    if min_price:
        products=products.filter(price__gte=min_price)
    if max_price:
        products=products.filter(price__lte=max_price)

    selected_colors=request.GET.get('colors','')
    if selected_colors:
        color_list=selected_colors.split(',')
        products=products.filter(
            variants__color__in=color_list
        )

    size=request.GET.get('size')
    if size:
        products=products.filter(
            variants__size=size
        )
    #Prevent duplicate products when matching multiple variants
    products=products.distinct()

    context = {
        'products': products,
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'selected_category': category or 'all',
        'selected_colors': selected_colors,
        'selected_size': size or '',
        'min_price': min_price or '0',
        'max_price': max_price or '4000',
    }

    if request.user.is_authenticated:
        user_wishlist = list(request.user.wishlist_items.values_list('product_id', flat=True))
    else:
        user_wishlist = []
    context['user_wishlist'] = user_wishlist

    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        return render(request, "product_grid.html",context)

    return render(request,'product_list.html',context)


#Views for Product Details
def product_detail(request,productID):
    product=get_object_or_404(Product, pk=productID)

    variants=product.variants.all()
    colors=variants.values_list('color',flat=True).distinct()
    sizes_raw = variants.values_list('size', flat=True).distinct()
    size_order = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5, 'XXL': 6}
    sizes = sorted(sizes_raw, key=lambda x: size_order.get(x, 99))

    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context={
        'product':product,
        'colors':colors,
        'sizes':sizes,
        'reviews': reviews,
        'review_form': ReviewForm(),
        'avg_rating': round(avg_rating, 1),
    }

    if request.user.is_authenticated:
        user_wishlist = list(request.user.wishlist_items.values_list('product_id', flat=True))
    else:
        user_wishlist = []
    context['user_wishlist'] = user_wishlist
    
    return render(request,'product_detail.html',context)


@login_required(login_url='/accounts_app/login/')
@require_POST
def toggle_wishlist(request, product_id):
    # Find the product
    product = get_object_or_404(Product, pk=product_id)
    # Look for the item in their model using the related_name
    wishlist_item = request.user.wishlist_items.filter(product=product).first()
    if wishlist_item:
        # If it exists, remove it (Toggle OFF)
        wishlist_item.delete()
        added = False
    else:
        # If it doesn't exist, create it in their model (Toggle ON)
        request.user.wishlist_items.create(product=product)
        added = True
    # Return JSON so the jQuery can update the heart and text
    return JsonResponse({'added': added})