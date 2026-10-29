from django.shortcuts import render


def payment_page(request):
    """Render the school-project payment page (demo only)."""
    return render(request, "payment_app/payment.html")
