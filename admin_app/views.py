from datetime import date
from django.shortcuts import render

def dashboard(request):
    context = {
        'today': date.today(),
        'pending_count': 3,
        'stats': {
            'revenue': 123745, 'revenue_delta': 12.4,
            'orders': 10, 'orders_delta': 8.1,
            'customers': 20, 'customers_delta': 2.3,
        },
        'sales': {
            '7': {'labels': ['Jun 1', 'Jun 2', 'Jun 3', 'Jun 4', 'Jun 5', 'Jun 6', 'Jun 7'],
                  'values': [3200, 4100, 3600, 5200, 4700, 6100, 7800]},
            '30': {'labels': [f'D{i}' for i in range(1, 31)],
                   'values': [2000, 3200, 4500, 3800, 3000, 4100, 5600, 5700, 6900, 8500,
                              7200, 6100, 5000, 4800, 5900, 6800, 7400, 8100, 7000, 6200,
                              5400, 4900, 5600, 6500, 7300, 7900, 7100, 6600, 7400, 8000]},
            '90': {'labels': [f'W{i}' for i in range(1, 14)],
                   'values': [12000, 14500, 13200, 16800, 15400, 18900, 17600,
                              20100, 19300, 22400, 21000, 24500, 26100]},
        },
        'top_products': [
            {'name': 'Graphic T-Shirt', 'category': 'Women', 'units': 48, 'share': 100,
             'image': 'store_app/images/products/tshirt.jpg'},
            {'name': 'New Balance Sneakers', 'category': 'All', 'units': 35, 'share': 73,
             'image': 'store_app/images/products/sneakers.jpg'},
            {'name': 'Zara Grey Hoodie', 'category': 'Men', 'units': 22, 'share': 46,
             'image': 'store_app/images/products/hoodie.jpg'},
        ],
        'orders': [
            {'id': 'VL12458', 'customer': 'Isabella Moreau', 'date': '2026/09/24', 'status': 'Processing', 'total': '7,857'},
            {'id': 'VL12457', 'customer': 'Simphwe Tshabalala', 'date': '2026/09/24', 'status': 'Processing', 'total': '1,245'},
            {'id': 'VL12456', 'customer': 'Tino Yanai', 'date': '2026/09/24', 'status': 'Shipped', 'total': '3,450'},
            {'id': 'VL12455', 'customer': 'Nkosi Sikelela', 'date': '2026/09/24', 'status': 'Delivered', 'total': '975'},
        ],
    }
    return render(request, 'admin_app/dashboard.html', context)
