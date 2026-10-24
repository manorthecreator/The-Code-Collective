import django.shortcuts

from django.shortcuts import render
from django.db.models import Sum, Q, Count, Avg, F 
from django.utils import timezone
from datetime import date, timedelta

from products_app.models import Product, Category, ProductVariant
from orders_app.models import Order, OrderItem      #don't have yet
from accounts_app.models import Customer    #don't have yet

def dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # 1. Stat Cards
    total_revenue = Order.objects.filter(status='Delivered').aggregate(total=Sum('totalPrice'))['total'] or 0
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()

    # 2. Top Selling Products
    top_products = Product.objects.annotate(
        units_sold=Sum('orderitem__quantity')
    ).order_by('-units_sold')[:3]

    # 3. Recent Orders
    recent_orders = Order.objects.select_related('customer').order_by('-orderDate')[:5]

    # 4. Pending Orders Count for Badge
    pending_count = Order.objects.filter(status='Pending').count()

    context = {
        'today': today,
        'stats': {
            'revenue': f"{total_revenue:,.2f}",
            'orders': total_orders,
            'customers': total_customers,
            'revenue_delta': 12,  # Dynamic calculation can be added based on previous period
            'orders_delta': 8,
            'customers_delta': -2,
        },
        'top_products': [
            {
                'name': p.name,
                'category': p.category.name if p.category else 'General',
                'units': p.units_sold or 0,
                'share': min(100, (p.units_sold or 0) * 5),
                'image': p.image.url if p.image else ''
            } for p in top_products
        ],
        'orders': [
            {
                'id': o.orderID,
                'customer': f"{o.customer.firstName} {o.customer.lastName}" if o.customer else "Guest",
                'date': o.orderDate.strftime('%Y/%m/%d'),
                'status': o.status,
                'total': f"{o.totalPrice:,.2f}"
            } for o in recent_orders
        ],
        'pending_count': pending_count,
        'sales': {
            '30': {
                'labels': ['May 14', 'May 18', 'May 22', 'May 26', 'May 30', 'Jun 3', 'Jun 7'],
                'values': [4000, 5200, 3100, 6800, 8200, 5400, 7900]
            }
        }
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
    customers_qs = Customer.objects.annotate(
        order_count=Count('order'),
        total_spent=Sum('order__totalPrice')
    ).all()

    context = {
        'customers': [
            {
                'name': f"{c.firstName} {c.lastName}",
                'email': c.user.email if hasattr(c, 'user') and c.user else '',
                'orders': c.order_count or 0,
                'spent': f"{c.total_spent or 0:,.2f}"
            } for c in customers_qs
        ]
    }
    return render(request, 'admin_app/customers.html', context)
   
def orders_view(request):
    status_filter = request.GET.get('status', 'all')
    orders_qs = Order.objects.select_related('customer').prefetch_related('items').order_by('-orderDate')

    if status_filter != 'all':
        orders_qs = orders_qs.filter(status__iexact=status_filter)

    context = {
        'orders': [
            {
                'id': f"VL{o.orderID}",
                'customer': f"{o.customer.firstName} {o.customer.lastName}" if o.customer else "Guest",
                'date': o.orderDate.strftime('%b %d, %Y'),
                'items': f"{o.items.count()} items",
                'status': o.status,
                'total': f"{o.totalPrice:,.2f}"
            } for o in orders_qs
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
    total_rev = Order.objects.filter(status='Delivered').aggregate(Sum('totalPrice'))['totalPrice__sum'] or 0
    order_count = Order.objects.count()
    avg_val = Order.objects.aggregate(Avg('totalPrice'))['totalPrice__avg'] or 0

    categories_breakdown = Category.objects.annotate(
        cat_total=Sum('product__orderitem__subtotal')
    )

    context = {
        'stats': {
            'revenue': f"{total_rev:,.2f}",
            'orders': order_count,
            'avg_order': f"{avg_val:,.2f}",
            'increase': '+ 24%',
        },
        'categories': [
            {
                'name': c.name,
                'amount': f"{c.cat_total or 0:,.2f}",
                'percentage': round(((c.cat_total or 0) / (total_rev or 1)) * 100, 1),
                'color': '#985922'
            } for c in categories_breakdown
        ],
        'top_products': Product.objects.all()[:3],
        'traffic_sources': [
            {'source': 'Direct', 'percentage': 38.7},
            {'source': 'Search Engines', 'percentage': 28.4},
            {'source': 'Social Media', 'percentage': 17.9},
            {'source': 'Email Campaigns', 'percentage': 9.6},
            {'source': 'Referrals', 'percentage': 5.4},
        ],
        'customer_insights': {
            'total': Customer.objects.count(),
            'new': Customer.objects.filter(user__createdDate__gte=timezone.now()-timedelta(days=30)).count() if hasattr(Customer, 'user') else 0,
            'returning': Customer.objects.annotate(c=Count('order')).filter(c__gt=1).count()
        }
    }
    return render(request, 'admin_app/analytics.html', context)