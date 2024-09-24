from django.shortcuts import render, redirect
from store.models import Product, Review
from django.db.models import Q
from django.contrib import messages


def home(request):
    popular_products = Product.objects.all().filter(is_available=True).order_by('-created_at')[:10]
    reviews = None
    for product in popular_products:
        reviews = Review.objects.filter(product_id=product.id, status=True)

    context = {
        'popular_products': popular_products,
        'reviews': reviews,
        'title': 'رستوران اول'
    }
    return render(request, 'index.html', context)


def search(request):
    try:
        if request.method == 'POST':
            search_text = request.POST['search_text'].lower()
            desired_products = Product.objects.filter(Q(name__icontains=search_text) | Q(name_fa__icontains=search_text))
            reviews = None
            for pdt in desired_products:
                reviews = Review.objects.filter(product_id=pdt.id, status=True)

            context = {
                'popular_products': desired_products,
                'reviews': reviews,
                'page_title': 'نتایج'
            }
            return render(request, 'index.html', context)
    except:
        messages.error(request, "مشکلی در روند جستجو اتفاق افتاد. دوباره زور بزن ...")
    return redirect(request.META.get('HTTP_REFERER'))