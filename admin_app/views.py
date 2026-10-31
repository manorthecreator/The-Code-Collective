from urllib import request

from django.shortcuts import redirect, render
from django.db.models import Sum, Q, Count, Avg, F, Max, DecimalField 
from django.db.models.functions import TruncDate
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta

from admin_app.forms import StoreSettingForm
from admin_app.models import StoreSetting
from products_app.models import Product, Category, ProductVariant

#safety net for missing models in case of import errors
try:
    from orders_app.models import Order, OrderItem
except (ImportError, ModuleNotFoundError, AttributeError):
    Order = None
    OrderItem = None

try:
    from accounts_app.models import Customer
except (ImportError, ModuleNotFoundError, AttributeError):
    Customer = None

LINE_TOTAL = F('unit_price') * F('quantity')

def sales_series(days):
    today = timezone.now().date()
    start = today - timedelta(days=days - 1)
    rows = (Order.objects.exclude(status='CANCELLED')
            .filter(created_at__date__gte=start)
            .annotate(day=TruncDate('created_at'))
            .values('day').annotate(t=Sum('total')))
    by_day = {r['day']: float(r['t']) for r in rows}
    labels, values = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        values.append(by_day.get(d, 0))
    return {'labels': labels, 'values': values}

def dashboard(request):
    today = timezone.now().date()

    # 1. Stat Cards & Recent Orders
    if Order:
        total_revenue = Order.objects.filter(status__iexact='Delivered').aggregate(total=Sum('total'))['total'] or 0
        total_orders = Order.objects.count()
        pending_count = Order.objects.filter(status__iexact='Pending').count()
        recent_orders = Order.objects.order_by('-created_at')[:5]
    else:
        total_revenue = 123745.00
        total_orders = 10
        pending_count = 2
        recent_orders = []

    # 2. Customers Count
    if Customer:
        total_customers = Customer.objects.count()
    else:
        total_customers = 20

    # 3. Top Selling Products
    if OrderItem:
        top_products = Product.objects.annotate(
            units_sold=Sum('orderitem__quantity')
        ).order_by('-units_sold')[:3]
    else:
        top_products = Product.objects.all()[:3]

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
        'top_products': [
            {
                'name': p.name,
                'category': p.category.name if getattr(p, 'category', None) else 'General',
                'units': getattr(p, 'units_sold', 12) or 0,
                'share': min(100, (getattr(p, 'units_sold', 12) or 0) * 5),
                'image': p.image.url if getattr(p, 'image', None) else ''
            } for p in top_products
        ],
        'orders': [
            {
                'id': f"VL{o.id}",
                'customer': getattr(o, 'customer_name', "Guest"),
                'date': o.created_at.strftime('%Y/%m/%d') if getattr(o, 'created_at', None) else today.strftime('%Y/%m/%d'),
                'status': getattr(o, 'status', 'Pending'),
                'total': f"{o.total:,.2f}" if isinstance(getattr(o, 'total', None), (int, float)) else str(getattr(o, 'total', '0.00'))
            } for o in recent_orders
        ] if recent_orders else [
            {'id': 'VL12458', 'customer': 'Isabella Moreau', 'date': '2026/09/24', 'status': 'Processing', 'total': '7,857.00'},
            {'id': 'VL12457', 'customer': 'Simphwe Tshabalala', 'date': '2026/09/24', 'status': 'Processing', 'total': '1,245.00'},
            {'id': 'VL12456', 'customer': 'Tino Yanai', 'date': '2026/09/24', 'status': 'Processing', 'total': '3,450.00'},
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
    # 1. Ensure default categories exist so the dropdown is never empty
    if Category and Category.objects.count() == 0:
        for cat_name in ['Women', 'Men', 'Accessories', 'Footwear']:
            Category.objects.get_or_create(name=cat_name)

    categories_qs = Category.objects.all() if Category else []

    # 2. Handle POST Request (Add Product)
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        status = request.POST.get('status', 'Available')
        stock = request.POST.get('stock', 0)
        image = request.FILES.get('image')

        category = Category.objects.filter(pk=category_id).first() if Category and category_id else None

        product = Product.objects.create(
            name=name,
            category=category,
            price=price,
            status=status,
            image=image
        )

        if ProductVariant and stock:
            ProductVariant.objects.create(
                product=product,
                size='Standard',
                color='Default',
                stockQuantity=int(stock)
            )

        return redirect('admin_app:products')

    # 3. Handle GET Request (Filtering & Search)
    category_id = request.GET.get('category', 'all')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')

    products_qs = Product.objects.select_related('category').annotate(
        total_stock=Sum('variants__stockQuantity')
    ).order_by('-productID' if hasattr(Product, 'productID') else '-id')

    if category_id != 'all':
        products_qs = products_qs.filter(category__pk=category_id)

    if status_filter != 'all':
        if status_filter == 'low-stock':
            products_qs = products_qs.filter(total_stock__gt=0, total_stock__lte=5)
        elif status_filter == 'out-of-stock':
            products_qs = products_qs.filter(Q(total_stock=0) | Q(total_stock__isnull=True))
        else:
            products_qs = products_qs.filter(status__iexact=status_filter)

    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    product_list = []
    for p in products_qs:
        stock = p.total_stock if p.total_stock is not None else 0
        
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
            'id': getattr(p, 'productID', p.pk),
            'sku': f"VRL-{getattr(p, 'productID', p.pk):03d}",
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
        'categories': categories_qs,
        'selected_category': category_id,
        'selected_status': status_filter,
        'search_query': search_query,
    }
    return render(request, 'admin_app/products.html', context)

def customers_view(request):
    # 1. Handle POST Request (Adding new customer)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if name and email:
            if Customer:
                # Save to database if Customer model exists
                name_parts = name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                Customer.objects.create(
                    firstName=first_name,
                    lastName=last_name,
                    email=email,
                    phone=phone
                )
            else:
                # Fallback: Save to session so new records display immediately
                session_customers = request.session.get('added_customers', [])
                session_customers.insert(0, {
                    'id': f"CUST-{100 + len(session_customers) + 1}",
                    'name': name,
                    'email': email,
                    'phone': phone or '+230 5000-0000',
                    'orders_count': 0,
                    'total_spent': '0.00',
                    'status': 'Active',
                    'joined': timezone.now().strftime('%b %d, %Y')
                })
                request.session['added_customers'] = session_customers
                request.session.modified = True

        return redirect('admin_app:customers')

    # 2. Handle GET Request (List & Search)
    search_query = request.GET.get('q', '').strip()

    if Customer:
        cust_qs = Customer.objects.all().order_by('-id')
        if search_query:
            cust_qs = cust_qs.filter(
                Q(firstName__icontains=search_query) |
                Q(lastName__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        customer_list = [
            {
                'id': f"CUST-{c.id:03d}",
                'name': f"{getattr(c, 'firstName', '')} {getattr(c, 'lastName', '')}".strip() or c.email,
                'email': c.email,
                'phone': getattr(c, 'phone', 'N/A'),
                'orders_count': getattr(c, 'order_set', None).count() if hasattr(c, 'order_set') else 0,
                'total_spent': '0.00',
                'status': 'Active',
                'joined': 'Oct 2026'
            } for c in cust_qs
        ]
    else:
        session_customers = request.session.get('added_customers', [])
        default_customers = [
            {'id': 'CUST-001', 'name': 'Isabella Moreau', 'email': 'isabella@example.com', 'phone': '+230 5123-4567', 'orders_count': 5, 'total_spent': '7,857.00', 'status': 'Active', 'joined': 'Jan 15, 2026'},
            {'id': 'CUST-002', 'name': 'Siphowe Tshabalala', 'email': 'siphowe@example.com', 'phone': '+230 5234-5678', 'orders_count': 2, 'total_spent': '1,245.00', 'status': 'Active', 'joined': 'Feb 20, 2026'},
            {'id': 'CUST-003', 'name': 'Tino Yanai', 'email': 'tino@example.com', 'phone': '+230 5345-6789', 'orders_count': 3, 'total_spent': '3,450.00', 'status': 'Active', 'joined': 'Mar 10, 2026'},
        ]
        customer_list = session_customers + default_customers

    if search_query and not Customer:
        customer_list = [
            c for c in customer_list
            if search_query.lower() in c['name'].lower() or search_query.lower() in c['email'].lower()
        ]

    context = {
        'customers': customer_list,
        'search_query': search_query,
    }
    return render(request, 'admin_app/customers.html', context)



def orders_view(request):
    status_filter = request.GET.get('status', 'all')

    if Order:
        orders_qs = Order.objects.order_by('-created_at')
        if status_filter != 'all':
            orders_qs = orders_qs.filter(status__iexact=status_filter)

        order_list = [
            {
                'id': f"VL{o.id}",
                'customer': getattr(o, 'customer_name', "Guest"),
                'date': o.created_at.strftime('%b %d, %Y') if getattr(o, 'created_at', None) else '',
                'items': f"{o.items.count()} items" if hasattr(o, 'items') and hasattr(o.items, 'count') else "1 item",
                'status': getattr(o, 'status', 'Pending'),
                'total': f"{o.total:,.2f}" if isinstance(getattr(o, 'total', None), (int, float)) else str(getattr(o, 'total', '0.00'))
            } for o in orders_qs
        ]
    else:
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
    settings_obj = StoreSetting.get_solo()

    if request.method == 'POST':
        form = StoreSettingForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store settings updated successfully!')
            return redirect('admin_app:settings')
        else:
            form = StoreSettingForm(instance=settings_obj)
            
    context = {
        'form': form,
        'settings': settings_obj,
    }
    return render(request, 'admin_app/settings.html', context)

def analytics_view(request):
    if Order:
        total_rev = Order.objects.filter(status__iexact='Delivered').aggregate(total=Sum('total'))['total'] or 0
        order_count = Order.objects.count()
        avg_val = Order.objects.aggregate(avg=Avg('total'))['avg'] or 0
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