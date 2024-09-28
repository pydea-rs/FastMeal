from .models import Cart, TakenProduct


def open_cart(request):
    # using this session code, program will id user's cart
    #  if no session_key is generated yet, then create one first
    cart_id = None
    try:
        if not request.session.session_key:  # solves the None session key error
            request.session.save()
        cart_id = request.session.session_key or request.session.create()

        if request.user.is_authenticated:
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
# THE USER SHPOULD BE ABLE TO HAVE MULTIPLE DIFFERENT cartS IN OTHER HANDS => ITS NOT NECESSARY!
def merge_user_carts(user):  # temporary approach
    try:
        # find all carts belonging to the same user
        carts_belonging_to_user = Cart.objects.filter(owner=user)
        # carts_belonging_to_user.sort(key=lambda x: x.created)  # sort by creation date ==> want to take the oldest
        # one and delete others
        merged_cart = carts_belonging_to_user[0]
        merged_cart_taken_products = TakenProduct.objects.filter(cart=merged_cart)

        if carts_belonging_to_user and len(carts_belonging_to_user) > 1:  # if umber of cart is one there's no need
            trash = []
            # removing carts directly will change the size of the carts_belonging_to_user, and causes trouble
            # so i save the un wanted carts in 'trash' and after that delete the items of trash one by one
            for cart in carts_belonging_to_user:
                if cart.ID() != merged_cart.ID():
                    if cart.owner is None and cart.worth == 0 and cart.discounts < 100:
                        trash.append(cart)
                    else:
                        products_taken_by_user = TakenProduct.objects.filter(cart=cart)
                        if products_taken_by_user:
                            for taken_product in products_taken_by_user:
                                taken_is_duplicate = False
                                # now check if there is a similar product with exact variation in the merged cart takens list
                                # if so just add the quantity of this one to the merged one and then delete this duplicate one
                                similar_products_in_merged_cart = merged_cart_taken_products.filter(product=taken_product.product)
                                for possibly_duplicate in similar_products_in_merged_cart:
                                    if possibly_duplicate.variation == taken_product.variation:
                                        possibly_duplicate.quantity += taken_product.quantity
                                        possibly_duplicate.save()
                                        taken_product.delete()
                                        taken_is_duplicate = True
                                        break

                                if not taken_is_duplicate:
                                    taken_product.cart = merged_cart
                                    taken_product.save()

                        trash.append(cart)
            for cart in trash:
                cart.delete()

            # remove empty carts:
            Cart.objects.filter(owner=None, cost=0).delete()
    except Exception as ex:
        print('sth went wrong while trying to merge carts: ' + ex.__str__())
