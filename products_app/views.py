from django.shortcuts import render,get_object_or_404
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
        .order_by('size')
    )
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
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        return render(request, "product_grid.html",context)

    return render(request,'product_list.html',context)


#Views for Product Details
def product_detail(request,productID):
    product=get_object_or_404(Product, pk=productID)

    variants=product.variants.all()
    colors=variants.values_list('color',flat=True).distinct()
    sizes=variants.values_list('size',flat=True).distinct()

    context={
        'product':product,
        'colors':colors,
        'sizes':sizes,
    }
    return render(request,'product_detail.html',context)