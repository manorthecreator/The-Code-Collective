import django.shortcuts

from django.shortcuts import render
from django.db.models import Sum, Q, Count, Avg, F 
from django.utils import timezone
from datetime import date, timedelta

from products_app.models import Product, Category, ProductVariant

#for erors since no have it yet
try:
    from orders_app.models import Order, OrderItem
    from accounts_app.models import Customer
except ImportError:
    Order = None
    OrderItem = None
    Customer = None

def dashboard(request):
    today = timezone.now().date()

    # 1. Stat Cards & Recent Orders (Safeguarded if Order model is None)
    if Order:
        total_revenue = Order.objects.filter(status='Delivered').aggregate(total=Sum('totalPrice'))['total'] or 0
        total_orders = Order.objects.count()
        pending_count = Order.objects.filter(status='Pending').count()
        recent_orders_qs = Order.objects.select_related('customer').order_by('-orderDate')[:5]
        orders_list = [
            {
                'id': o.orderID,
                'customer': f"{o.customer.firstName} {o.customer.lastName}" if getattr(o, 'customer', None) else "Guest",
                'date': o.orderDate.strftime('%Y/%m/%d'),
                'status': o.status,
                'total': f"{o.totalPrice:,.2f}"
            } for o in recent_orders_qs
        ]
    else:
        total_revenue = 123745.00
        total_orders = 10
        pending_count = 2
        orders_list = [
            {'id': 'VL12458', 'customer': 'Isabella Moreau', 'date': '2026/09/24', 'status': 'Processing', 'total': '7,857'},
            {'id': 'VL12457', 'customer': 'Simphwe Tshabalala', 'date': '2026/09/24', 'status': 'Processing', 'total': '1,245'},
            {'id': 'VL12456', 'customer': 'Tino Yanai', 'date': '2026/09/24', 'status': 'Processing', 'total': '3,450'},
            {'id': 'VL12455', 'customer': 'Nkosi sikelela', 'date': '2026/09/24', 'status': 'Active', 'total': '975'},
        ]

    # 2. Total Customers
    if Customer:
        total_customers = Customer.objects.count()
    else:
        total_customers = 20

    # 3. Top Selling Products
    if OrderItem:
        top_products_qs = Product.objects.annotate(
            units_sold=Sum('orderitem__quantity')
        ).order_by('-units_sold')[:3]
        top_products_list = [
            {
                'name': p.name,
                'category': p.category.name if p.category else 'General',
                'units': p.units_sold or 0,
                'share': min(100, (p.units_sold or 0) * 5),
                'image': p.image.url if p.image else ''
            } for p in top_products_qs
        ]
    else:
        top_products_list = [
            {'name': 'Graphic T-Shirt', 'category': 'Women', 'units': 42, 'share': 80, 'image': ''},
            {'name': 'New Balance Sneakers', 'category': 'Shoes', 'units': 28, 'share': 55, 'image': ''},
        ]

    context = {
        'today': today,
        'stats': {
            'revenue': f"{total_revenue:,.2f}" if isinstance(total_revenue, (int, float)) else str(total_revenue),
            'orders': total_orders,
            'customers': total_customers,
            'revenue_delta': 12,
            'orders_delta': 8,
            'customers_delta': -2,
        },
        'top_products': top_products_list,
        'orders': orders_list,
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
    if Customer:
        customers_qs = Customer.objects.annotate(
            order_count=Count('order'),
            total_spent=Sum('order__totalPrice')
        ).all()

        customer_list = [
            {
                'name': f"{c.firstName} {c.lastName}",
                'email': c.user.email if hasattr(c, 'user') and c.user else '',
                'orders': c.order_count or 0,
                'spent': f"{c.total_spent or 0:,.2f}"
            } for c in customers_qs
        ]
    else:
        # Fallback placeholder data until accounts_app is merged
        customer_list = [
            {'name': 'Isabella Moretti', 'email': 'isabella@example.com', 'orders': 5, 'spent': '1,640.00'},
            {'name': 'John Doe', 'email': 'john.doe@example.com', 'orders': 12, 'spent': '3,936.00'},
            {'name': 'Henry Pulga', 'email': 'henry.pulga@example.com', 'orders': 7, 'spent': '2,296.00'},
            {'name': 'Pablo Gavi', 'email': 'pablo.gavi@example.com', 'orders': 2, 'spent': '656.00'},
            {'name': 'Cole Palmer', 'email': 'cole.palmer@example.com', 'orders': 1, 'spent': '328.00'},
        ]

    context = {'customers': customer_list}
    return render(request, 'admin_app/customers.html', context)


def orders_view(request):
    status_filter = request.GET.get('status', 'all')

    if Order:
        orders_qs = Order.objects.select_related('customer').prefetch_related('items').order_by('-orderDate')
        if status_filter != 'all':
            orders_qs = orders_qs.filter(status__iexact=status_filter)

        order_list = [
            {
                'id': f"VL{o.orderID}",
                'customer': f"{o.customer.firstName} {o.customer.lastName}" if getattr(o, 'customer', None) else "Guest",
                'date': o.orderDate.strftime('%b %d, %Y'),
                'items': f"{o.items.count()} items",
                'status': o.status,
                'total': f"{o.totalPrice:,.2f}"
            } for o in orders_qs
        ]
    else:
        # Fallback placeholder data until orders_app is merged
        order_list = [
            {'id': '12456', 'customer': 'Isabella Moretti', 'date': 'Jun 12, 2026', 'items': '3 items', 'status': 'Pending', 'total': '328.00'},
            {'id': '12457', 'customer': 'John Doe', 'date': 'Jun 12, 2026', 'items': '4 items', 'status': 'Processing', 'total': '328.00'},
            {'id': '12458', 'customer': 'Henry Pulga', 'date': 'Jun 12, 2026', 'items': '7 items', 'status': 'Shipped', 'total': '328.00'},
            {'id': '12476', 'customer': 'Pablo Gavi', 'date': 'Jun 12, 2026', 'items': '2 items', 'status': 'Delivered', 'total': '328.00'},
            {'id': '12482', 'customer': 'Ven Paredes', 'date': 'Jun 12, 2026', 'items': '9 items', 'status': 'Cancelled', 'total': '328.00'},
            {'id': '12426', 'customer': 'Cole Palmer', 'date': 'Jun 12, 2026', 'items': '1 item', 'status': 'Processing', 'total': '328.00'},
        ]

    context = {'orders': order_list}
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
    return render(request, 'admin_app/settings.html', context)

def analytics_view(request):
    if Order:
        total_rev = Order.objects.filter(status='Delivered').aggregate(Sum('totalPrice'))['totalPrice__sum'] or 0
        order_count = Order.objects.count()
        avg_val = Order.objects.aggregate(Avg('totalPrice'))['totalPrice__avg'] or 0
    else:
        total_rev = 38402.00
        order_count = 30
        avg_val = 1280.07

    if Category and OrderItem:
        categories_breakdown = Category.objects.annotate(
            cat_total=Sum('product__orderitem__subtotal')
        )
        categories_list = [
            {
                'name': c.name,
                'amount': f"{getattr(c, 'cat_total', 0) or 0:,.2f}",
                'percentage': round(((getattr(c, 'cat_total', 0) or 0) / (total_rev or 1)) * 100, 1),
                'color': '#985922'
            } for c in categories_breakdown
        ]
    else:
        categories_list = [
            {'name': 'Women', 'amount': '128,450.30', 'percentage': 51.6, 'color': '#985922'},
            {'name': 'Men', 'amount': '72,680.40', 'percentage': 29.2, 'color': '#d3a172'},
            {'name': 'Accessories', 'amount': '47,629.80', 'percentage': 19.2, 'color': '#e8d5c4'},
        ]

    if Customer:
        total_cust = Customer.objects.count()
        returning_cust = Customer.objects.annotate(c=Count('order')).filter(c__gt=1).count()
    else:
        total_cust = 174455
        returning_cust = 161468

    context = {
        'stats': {
            'revenue': f"{total_rev:,.2f}" if isinstance(total_rev, (int, float)) else str(total_rev),
            'orders': order_count,
            'avg_order': f"{avg_val:,.2f}" if isinstance(avg_val, (int, float)) else str(avg_val),
            'increase': '+ 24%',
        },
        'categories': categories_list,
        'top_products': Product.objects.all()[:3],
        'traffic_sources': [
            {'source': 'Direct', 'percentage': 38.7},
            {'source': 'Search Engines', 'percentage': 28.4},
            {'source': 'Social Media', 'percentage': 17.9},
            {'source': 'Email Campaigns', 'percentage': 9.6},
            {'source': 'Referrals', 'percentage': 5.4},
        ],
        'customer_insights': {
            'total': f"{total_cust:,}" if isinstance(total_cust, int) else total_cust,
            'new': "12,987",
            'returning': f"{returning_cust:,}" if isinstance(returning_cust, int) else returning_cust
        }
    }
    return render(request, 'admin_app/analytics.html', context)

