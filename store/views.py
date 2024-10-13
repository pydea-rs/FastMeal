import json

from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from .models import Product, Review, Gallery
from .forms import ReviewForm
from restaurant.models import Restaurant
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json


def store(request, category_filter=None):
    max_price = min_price = 0
    selected_category: Category|None = None
    selected_restaurant: Restaurant|None = None
    try:
        if category_filter:
            selected_category = get_object_or_404(Category, slug=category_filter)
        restaurant_filter = request.GET.get('restaurant')
        if restaurant_filter:
            selected_restaurant = get_object_or_404(Restaurant, slug=restaurant_filter)

        if selected_category and restaurant_filter:
            products = Product.objects.filter(category_id=selected_category.id, restaurant_id=selected_restaurant.id)
        elif selected_category:
            products = Product.objects.filter(category_id=selected_category.id)
        elif selected_restaurant:
            products = Product.objects.filter(restaurant_id=selected_restaurant.id)
        else:
            products = Product.objects.all()
        if request.method == "POST":
            try:
                min_price = int(request.POST["min_price"])
            except:
                min_price = 0

            try:
                max_price = int(request.POST["max_price"])
            except:
                max_price = 0

            if min_price > 0:
                products = list(filter(lambda p: p.variation_set.is_expensive_than(min_price), products))
            if max_price > 0:
                products = list(filter(lambda p: p.variation_set.is_cheaper_than(max_price), products))

    except Exception as ex:
        print(ex.__str__())
        products = []

    context = {
        'products': products,
        'products_count': products.count if products else 0,
        'category_filter': selected_category,
        'restaurant_filter': selected_restaurant,
        'max_price': max_price,
        'min_price': min_price,
        'restaurants': Restaurant.objects.all()
    }

    return render(request, 'store/store.html', context)


def product(request, category_filter, product_slug=None):
    context = dict()
    try:
        this_product = Product.objects.get(slug=product_slug, category__slug=category_filter)
        reviews = Review.objects.filter(product=this_product,)
        gallery = Gallery.objects.filter(product=this_product)
        context = {
            'this_product': this_product,
            'variations': this_product.variation_set.all,
            'variations_json': json.dumps(this_product.variation_set.specifics),
            'reviews': reviews,
            'gallery': gallery,
        }
    except Exception as ex:
        raise ex

    return render(request, 'store/product.html', context)


@login_required(login_url='login')
def post_review(request, product_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                # ّFIXME: This is a little idiotic i think
                #  , i think its better user be able to put multiple comments on each product
                old_review = Review.objects.get(author__id=request.user.id, product__id=product_id)
                form = ReviewForm(request.POST, instance=old_review)  # instance=review parameter will prevent from
                # django from creating new review, and it will replace existing one
                form.save()
                messages.info(request, "نظر شما در باره این آیتم به روز رسانی شد.")
            except Review.DoesNotExist:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    try:
                        product_to_be_reviewed = Product.objects.get(id=product_id)
                        new_review = Review(product=product_to_be_reviewed, author=request.user,
                                            comment=form.cleaned_data['comment'], rating=form.cleaned_data['rating'],
                                            ip=request.META.get('REMOTE_ADDR'))
                        # validate form and ip first
                        new_review.save()
                        messages.success(request, 'نظر شما ثبت شد.')
                    except Product.DoesNotExist:
                        messages.error(request, 'شما در حال نظر دادن در رابطه با کالایی هستید که وجود خارجی ندارد!')
    else:
        messages.error(request, 'برای ارسال نظر باید ابتدا وارد حساب کاربری خود شوید.')
    return redirect(request.META.get('HTTP_REFERER'))


