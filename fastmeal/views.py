from django.shortcuts import render, redirect
from store.models import Product, Review
from restaurant.models import Restaurant
from django.db.models import Q
from django.contrib import messages
from typing import List, Dict


class FeedSection:
    def __init__(self, restaurant: Restaurant, products: List[Product]):
        self.restaurant = restaurant
        self.products = products


def home(request):
    restaurants = Restaurant.objects.filter().order_by('-created_at')  # Order by rating.
    feed: List[FeedSection] = list(map(
        lambda restaurant: FeedSection(restaurant, Product.objects.filter(restaurant_id=restaurant.id, is_available=True).order_by('-created_at')[:10]),
        restaurants))

    context = {
        'feed': feed,
    }
    return render(request, 'index.html', context)


def search(request):
    try:
        if request.method == 'POST':
            search_text = request.POST['search_text'].lower()
            desired_products = Product.objects.filter(
                Q(name__icontains=search_text) | Q(name_fa__icontains=search_text)
            )
            restaurants = set(map(lambda product: product.restaurant, desired_products))
            search_feed = list(
                map(
                    lambda rest: FeedSection(rest, list(filter(lambda p: p.restaurant.id == rest.id, desired_products))),
                    restaurants
                )
            )
            context = {
                'feed': search_feed,
            }
            return render(request, 'index.html', context)
    except:
        messages.error(request, "مشکلی در روند جستجو اتفاق افتاد. لطفا دوباره تلاش کنید ...")
    return redirect(request.META.get('HTTP_REFERER'))