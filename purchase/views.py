from django.shortcuts import render, redirect
from cart.models import TakenProduct
from .forms import OrderForm, ReserveTransactionForm
from cart.utlities import open_cart
from .models import Order, DeliveryInfo, Transaction, PurchasedItem, Receipt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from devshare.models import DevShare
from user.models import User


def finalize_order(request, order_key, method, status, reference_id=None, amount=None):
    order = None
    try:
        order = Order.objects.get(owner=request.user, key=order_key)
        if order:
            order.verified = status.lower()
            # now we ship the taken product items to ordered product items
            user_cart = open_cart(request)
            user_cart.submit_bill()  # to make sure total products in the cart are billed successfully
            cart_items = TakenProduct.objects.filter(cart=user_cart)
            for item in cart_items:
                purchased_item = PurchasedItem()
                purchased_item.order_id = order.id  # another way of setting an ForeignKey object's value inside a
                # model
                purchased_item.buyer_id = request.user.id
                purchased_item.product_id = item.product_id
                # variations cannot be set like this, it must be set after .save() call
                purchased_item.quantity = item.quantity
                purchased_item.cost = item.total_absolute_price()
                purchased_item.delivered = order.verified == 'delivered'
                purchased_item.variation = item.variation
                purchased_item.save()

                if purchased_item.product.is_available and purchased_item.variation.is_available:
                    purchased_item.save()
                    item.delete()
                else:
                    order.verified = "failed"
            order.save()
            user_cart.delete()
            return order
        else:
            print('No order has been found')
    except Exception as ex:
        print(f'sth went wrong while saving the transaction cause: {ex}')
        if order:
            order.save()
    # TODO: What happens if this is called with n order?


def get_delivery_info(user: User, form: OrderForm) -> DeliveryInfo:
    try:
        info = DeliveryInfo.objects.get(user=user, phone=form.cleaned_data['phone'])
    except ObjectDoesNotExist:
        info = DeliveryInfo()
        info.phone = form.cleaned_data['phone']
        info.user = user

    info.location = form.cleaned_data['location']
    info.notes = form.cleaned_data['notes'] or None
    info.save()
    return info


@login_required(login_url='login')
def submit_order(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')

        user = request.user
        user_cart = open_cart(request)
        user_cart.submit_bill()  # to make sure total products in the cart are billed successfully
        cart_items = TakenProduct.objects.filter(cart=user_cart)
        # use cart_items or add a quantity field to cart model?
        if cart_items.count() <= 0:
            return redirect('store')

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                # first get the data posted by user
                order = Order()
                
                order.receiver = get_delivery_info(user, form)

                order.cost = user_cart.worth
                order.discounts = user_cart.discounts
                order.shipping_cost = 5000  # FIXME: How this should get calculated?

                order.owner = user
                order.owner.ip = request.META.get('REMOTE_ADDR')
                order.owner.save()
                order.save()  # save object and create id field for it (to use in keygen)
                order.key = order.keygen()
                order.save()  # call save for django to set the id primary key automatically
                new_share = DevShare(order=order)
                new_share.calculate()
                new_share.save()
                # use Order.objects.get to make sure that the order is saved properly and retrievable
                order = Order.objects.get(owner=request.user, key=order.key)
                context = {
                    'order': order,
                    'goods': cart_items,
                }
                return render(request, 'purchase/preview.html', context)
    except Exception as ex:
        print('sth went wrong while processing the order cause: ' + ex.__str__())

    return redirect('order')


@login_required(login_url='login')
def preview(request):
    return render(request, 'purchase/preview.html')


@login_required(login_url='login')
def check_order(request, order_key):
    order = finalize_order(request=request, order_key=order_key, method='receipt', status='pending')
    if order and order.verified.lower() == "pending":
        # now we send the user to transaction page

        return redirect(order.receipt_url())
        # return render(request, 'purchase/receipt.html', context)
    # sth went wrong: HANDLE ERROR
    return render(request, 'purchase/preview.html')


# ACTUALLY THIS METHOD MUST BE CALLED BY ADIM SIDE
@login_required(login_url="login")
def accept_order(request, order_key):
    order = None
    try:
        order = Order.objects.get(key=order_key, owner=request.user)
        if request.user and request.user.is_authenticated and order_key:
            if order and order.verified.lower() == "certified":
                order.sell_products()
                #  saves automatically in function above

        # send proper error
    except Exception as ex:
        order = None
        print('sth went wrong while showing the order final details: ' + ex.__str__())
    return render(request, 'purchase/result.html', {"order": order})


@login_required(login_url='login')
def take_receipt(request, order_key):
    user = request.user
    if user and user.is_authenticated:
        order = Order.objects.get(owner=user, key=order_key)
        if order:
            context = {'order': order}
            return render(request, 'purchase/receipt.html', context)
    return render(request, 'purchase/receipt.html')


def reserve_order(request):
    if request.method == "POST":
        form = ReserveTransactionForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = Receipt(reference_id=form.cleaned_data['reference_id'], image=form.cleaned_data['image'],
                              amount=form.cleaned_data['amount'], order_key=form.cleaned_data['order_key'])
            receipt.save()
            transaction = Transaction(source=request.user, method="reserve", validation="pending", receipt=receipt)
            transaction.save()
            order = Order.objects.get(key=form.cleaned_data["order_key"], owner=request.user)
            if order:
                order.transaction = transaction
                order.save()
            return redirect(order.accept_url())
        return redirect('home')
