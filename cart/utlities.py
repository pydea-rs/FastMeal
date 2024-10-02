from .models import Cart, TakenProduct


def open_cart(request):
    # using this session code, program will id user's cart
    #  if no session_key is generated yet, then create one first
    cart_id = None
    try:
        if not request.session.session_key:  # solves the None session key error
            request.session.save()
        cart_id = request.session.session_key or request.session.create()

        if request.user and request.user.is_authenticated:
            if Cart.objects.all():
                merge_user_carts(request.user)
                current_cart = Cart.objects.filter(owner=request.user)
                # TEMP ***************
                if not current_cart:
                    raise Cart.DoesNotExist
                current_cart = current_cart[0]
            else:
                raise Cart.DoesNotExist

        else:
            current_cart = Cart.objects.get(sid=cart_id)  # recent opened cart
            if request.user.is_authenticated:
                current_cart.owner = request.user

    except Cart.DoesNotExist:
        current_cart = Cart.objects.create(sid=cart_id, owner=request.user if request.user.is_authenticated else None)
    return current_cart


def attach_current_cart_to_current_user(request, user):
    try:
        cart = Cart.objects.get(sid=open_cart(request).ID())
        if cart is not None:
            cart.owner = user
            cart.save()
    except:
        print('no opened cart found to attach')


# # # CHECK THIS METHOD WORKS CORRECTLY NOTE: MERGING cartS IS A SOLUTION FOR NOW ACTUALLY ==> I HAVE IN MIND THAT
# THE USER SHOULD BE ABLE TO HAVE MULTIPLE DIFFERENT cartS IN OTHER HANDS => IT'S NOT NECESSARY!
def merge_user_carts(user):  # temporary approach
    try:
        carts_belonging_to_user = Cart.objects.filter(owner=user)

        if carts_belonging_to_user and carts_belonging_to_user.count() > 1:  # if umber of cart is one there's no need
            merged_cart = carts_belonging_to_user[0]
            merged_cart_taken_products = TakenProduct.objects.filter(cart=merged_cart)

            for cart in carts_belonging_to_user:
                if cart.ID() != merged_cart.ID():
                    if cart.owner is not None and (cart.worth != 0 or cart.discounts == 100):
                        cart_contents = TakenProduct.objects.filter(cart=cart)

                        for taken_product in cart_contents:
                            similar_product_in_merged_cart = merged_cart_taken_products.get(
                                        product_id=taken_product.product.id, variation_id=taken_product.variation.id
                            )
                            if similar_product_in_merged_cart:
                                similar_product_in_merged_cart.quantity += taken_product.quantity
                                similar_product_in_merged_cart.save()
                                taken_product.delete()
                            else:
                                taken_product.cart = merged_cart
                                taken_product.save()

                    cart.owner = None
                    cart.worth = 0
                    cart.save()

            Cart.objects.filter(owner=None).delete()
            Cart.objects.filter(worth=0, discounts__lt=100).delete()
    except Exception as ex:
        print('sth went wrong while trying to merge carts: ' + ex.__str__())
