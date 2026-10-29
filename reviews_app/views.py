from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from products_app.models import Product
from .forms import ReviewForm

def submit_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            
            return JsonResponse({
                'success': True,
                'name': review.name,
                'rating': review.rating,
                'comment': review.comment,
            })
        else:
            # THIS WILL PRINT THE FORM ERRORS IN OUR TERMINAL
            print("FORM ERRORS:", form.errors) 
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)