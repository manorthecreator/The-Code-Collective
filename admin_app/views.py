from urllib import request

import django.shortcuts

from django.shortcuts import render
from django.db.models import Sum, Q, Count, Avg, F 
from django.utils import timezone
from datetime import date, timedelta
from matplotlib.style import context

from products_app.models import Product, Category, ProductVariant
#from orders_app.models import Order, OrderItem      #don't have yet
#from accounts_app.models import Customer    #don't have yet

def dashboard(request):
      context = {
          'today': timezone.now().date(),
          'stats': {'revenue': '184,200', 'orders': 312, 'customers': 1204,
                    'revenue_delta': 12, 'orders_delta': 8, 'customers_delta': -2},
          'top_products': [],
          'orders': [
              {'id': 1042, 'customer': 'Amina R.', 'date': '2026/10/24', 'status': 'Processing', 'total': '3,450.00'},
              {'id': 1041, 'customer': 'Kevin M.', 'date': '2026/10/23', 'status': 'Shipped', 'total': '1,980.00'},
          ],
          'pending_count': 3,
          'sales': {'30': {'labels': ['Oct 1', 'Oct 8', 'Oct 15', 'Oct 22'],
                           'values': [4000, 5200, 3100, 6800]},
                    '7': {'labels': ['Mon', 'Tue', 'Wed'], 'values': [2000, 3000, 2500]},
                    '90': {'labels': ['Aug', 'Sep', 'Oct'], 'values': [4000, 6000, 8000]}},
      }
      return render(request, 'admin_app/dashboard.html', context)


def products_view(request):
    # Retrieve query parameters from request GET
    category_id = request.GET.get('category', 'all')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')

    # Base QuerySet with Category select_related and variant stock aggregation
    products_qs = Product.objects.select_related('category').annotate(
        total_stock=Sum('variants__stockQuantity')
    ).order_by('-productID')

    # Apply Category Filter
    if category_id != 'all':
        products_qs = products_qs.filter(category__categoryID=category_id)

    # Apply Status Filter
    if status_filter != 'all':
        if status_filter == 'low-stock':
            products_qs = products_qs.filter(total_stock__gt=0, total_stock__lte=5)
        elif status_filter == 'out-of-stock':
            products_qs = products_qs.filter(Q(total_stock=0) | Q(total_stock__isnull=True))
        else:
            products_qs = products_qs.filter(status__iexact=status_filter)

    # Apply Search Filter
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Format list for rendering in template
    product_list = []
    for p in products_qs:
        stock = p.total_stock if p.total_stock is not None else 0
        
        # Determine dynamic stock/status badge
        if p.status == 'Unavailable':
            display_status = 'Unavailable'
            status_class = 'is-unavailable'
        elif stock == 0:
            display_status = 'Out of Stock'
            status_class = 'is-out'
        elif stock <= 5:
            display_status = 'Low Stock'
            status_class = 'is-low'
        else:
            display_status = 'Available'
            status_class = 'is-available'

        product_list.append({
            'id': p.productID,
            'sku': f"VRL-{p.productID:03d}",
            'name': p.name,
            'category_name': p.category.name if p.category else 'Uncategorized',
            'price': f"{p.price:.2f}",
            'stock': stock,
            'image_url': p.image.url if p.image else '',
            'display_status': display_status,
            'status_class': status_class,
        })

    context = {
        'products': product_list,
        'categories': Category.objects.all(),
        'selected_category': category_id,
        'selected_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_app/products.html', context)

def customers_view(request):
    context = {
        'customers': [
            {'name': 'Amina Rahman', 'email': 'amina@example.com', 'orders': 5, 'spent': '12,400.00'},
            {'name': 'Kevin Moorghen', 'email': 'kevin@example.com', 'orders': 2, 'spent': '3,980.00'},
        ]
    }
    return render(request, 'admin_app/customers.html', context)
   
def orders_view(request):
    context = {
        'orders': [
            {'id': 'VL1042', 'customer': 'Amina Rahman', 'date': 'Oct 24, 2026',
             'items': '3 items', 'status': 'Processing', 'total': '3,450.00'},
            {'id': 'VL1041', 'customer': 'Kevin Moorghen', 'date': 'Oct 23, 2026',
             'items': '1 items', 'status': 'Shipped', 'total': '1,980.00'},
        ]
    }
    return render(request, 'admin_app/orders.html', context)

def settings_view(request):
    context = {
        'settings': {
            'store_name': 'Velora',
            'store_email': 'hello@velora.com',
            'phone': '+230 1234-5678',
            'currency': 'Rs MUR',
            'timezone': '(GMT +4:00) Mauritius Standard Time',
            'legal_name': 'Velora Fashion LTD',
            'description': 'Velora is a modern fashion brand inspired by elegance, individuality, and timeless style.',
            'address': '123 Fashion Ave, 5th Floor',
            'city': 'Rose Hill',
            'state': 'Mauritius',
        }
    }
    return django.shortcuts.render(request, 'admin_app/settings.html', context)

def analytics_view(request):
    context = {
        'stats': {'revenue': '184,200.00', 'orders': 312, 'avg_order': '590.38', 'increase': '+ 24%'},
        'categories': [
            {'name': 'Clothing', 'amount': '90,000.00', 'percentage': 48.9, 'color': '#985922'},
            {'name': 'Shoes', 'amount': '60,000.00', 'percentage': 32.6, 'color': '#985922'},
        ],
        'top_products': Product.objects.all()[:3],
        'traffic_sources': [
            {'source': 'Direct', 'percentage': 38.7},
            {'source': 'Search Engines', 'percentage': 28.4},
            {'source': 'Social Media', 'percentage': 17.9},
        ],
        'customer_insights': {'total': 1204, 'new': 41, 'returning': 380},
    }
    return render(request, 'admin_app/analytics.html', context)