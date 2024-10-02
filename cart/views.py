from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, TakenProduct
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .utlities import open_cart
from django.contrib import messages


def submit_preferred_variation(variation, taken=None, product=None, current_cart=None):
    if variation:
        if not taken:
            if product and current_cart:
                taken = TakenProduct.objects.create(product=product, cart=current_cart, variation=variation)
            elif not product:
                raise TakenProduct.DoesNotExist('Unknown product. cannot create a new Taken field')
            elif not current_cart:
                raise Cart.DoesNotExist('User does not have available cart.')
        taken.quantity = 1
        taken.save()
    else:
        raise Variation.DoesNotExist('Product variation must always be selected.')


def put_back(request, product_id, taken_item_id):
    product = get_object_or_404(Product, id=product_id)
    current_cart = None
    try:
        current_cart = open_cart(request)
        taken = TakenProduct.objects.get(id=taken_item_id, product=product, cart=current_cart)
        taken.decrement_quantity()
        taken.save()

    except TakenProduct.DoesNotExist:
        # handle this error (actually it must never happen
        # WRITE A METHOD TO CALCULATE COST CORRECTLY
        pass
    except ObjectDoesNotExist:
        pass
    return redirect("cart")


def put_all(request, product_id, taken_item_id, ):
    product = get_object_or_404(Product, id=product_id)
    current_cart = None
    try:
        current_cart = open_cart(request)
        TakenProduct.objects.get(id=taken_item_id, product=product, cart=current_cart).delete()

    except TakenProduct.DoesNotExist:
        # handle this error (actually it must never happen
        # WRITE A METHOD TO CALCULATE COST CORRECTLY
        pass
    except ObjectDoesNotExist:
        pass
    return redirect("cart")


def take_another(request, product_id, taken_item_id):
    product = Product.objects.get(id=product_id)
    current_cart = None
    try:
        current_cart = open_cart(request)
        taken = TakenProduct.objects.get(id=taken_item_id, product=product, cart=current_cart)
        taken.increment_quantity()
        taken.save()
    except TakenProduct.DoesNotExist:
        taken = TakenProduct.objects.create(product=product, cart=current_cart, quantity=1, total_price=product.price)
        taken.save()
    except ObjectDoesNotExist:
        # handle this error seriously
        pass
    return redirect("cart")


def take_product(request, product_id):
    product = Product.objects.get(id=product_id)
    variation = None
    current_page = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        if 'variation' not in request.POST:
            messages.error(f'نوع {product} مشخص نشده است.')
            return redirect(current_page)

        variation = request.POST['variation']

        try:
            variation = Variation.objects.get(product=product, id=variation)
            if not variation.is_available:
                messages.error(request, "این کالا موجود نیست!")
                return redirect(current_page)
        except:  # such as csrf_token
            pass

        current_cart = None
        try:
            current_cart = open_cart(request)
            try:
                taken = TakenProduct.objects.get(variation=variation, cart=current_cart)
            except:
                taken = None

            if not taken or not taken.quantity:
                submit_preferred_variation(taken=taken, variation=variation, product=product,
                                           current_cart=current_cart)
            else:
                # SHOW ERROR MESSAGE

                return redirect('cart')
        except TakenProduct.DoesNotExist:
            # handle this error (actually it must never happen
            submit_preferred_variation(variation=variation, product=product, current_cart=current_cart)

        except ObjectDoesNotExist:
            # handle this error seriously
            pass
        # handle all errors
    return redirect('cart')


def get_cart(request):
    try:
        context = open_cart(request).submit_bill()
    except ObjectDoesNotExist:
        # meaning cart does not exist
        context = {
            'taken_products': [],
            'cart': None,
        }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def order(request):
    try:
        context = open_cart(request).submit_bill()
    except ObjectDoesNotExist:
        # meaning cart does not exist
        context = {
            'taken_products': [],
            'cart': None,
        }
    return render(request, 'purchase/order.html', context)
