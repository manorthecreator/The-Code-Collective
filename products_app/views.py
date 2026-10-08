from django.shortcuts import render
from .models import Product,Category,ProductVariant

# Create your views here.

def product_list(request):
    products = Product.objects.filter(status='Available')
    categories = Category.objects.all()
    colors=(
        ProductVariant.objects
        .values('color', 'colorCode')
        .distinct()
    )
    sizes=(
        ProductVariant.objects
        .values_list('size', flat=True)
        .distinct()
    )
    category = request.GET.get("category")
    if category and category != "all":
        products = products.filter(category_id=category)

    return render(request, "product_list.html", {
        "products": products,
        "categories": categories,
        "colors": colors,
        "sizes": sizes,
        "selected_category": category or "all",
    })