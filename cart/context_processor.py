from .models import Cart, TakenProduct
from .utlities import open_cart


def cart_counter(request):
    count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = open_cart(request)

            if request.user.is_authenticated:
                items = TakenProduct.objects.all().filter(cart__owner=request.user)
            else:
                items = TakenProduct.objects.all().filter(cart=cart)

            count = len(items)
        except:
            count = 0

    return dict(cart_counter=count)
