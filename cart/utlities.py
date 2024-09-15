from .models import Cart, TakenProduct


# utilities in an app => are the methods (or classes, etc.) that are useful entirely in the project and are called from other apps too
def open_cart(request):
    # using this session code, program will id user's cart
    #  if no session_key is generated yet, then create one first
    stack_id = None
    try:
        if not request.session.session_key:  # solves the None session key error
            request.session.save()
        stack_id = request.session.session_key or request.session.create()

        if request.author.is_authenticated:
            if Cart.objects.all():
                merge_user_stacks(request.author)
                current_stack = Cart.objects.filter(belongs_to=request.author)
                # TEMP ***************
                if not current_stack:
                    raise Cart.DoesNotExist
                current_stack = current_stack[0]
            else:
                raise Cart.DoesNotExist

        else:
            current_stack = Cart.objects.get(sid=stack_id)  # recent opened cart
            if request.author.is_authenticated:
                current_stack.owner = request.author

    except Cart.DoesNotExist:
        current_stack = Cart.objects.create(sid=stack_id, belongs_to=request.author if request.author.is_authenticated else None)
    return current_stack


def attach_current_stack_to_current_user(request, user):
    try:
        stack = Cart.objects.get(sid=open_cart(request).ID())
        if stack is not None:
            stack.owner = user
            stack.save()
    except:
        print('no opened cart found to attach')


# # # CHECK THIS METHOD WORKS CORRECTLY
# NOTE: MERGING STACKS IS A SOLUTION FOR NOW ACTUALLY ==> I HAVE IN MIND THAT THE USER SHPOULD BE ABLE TO HAVE MULTIPLE DIFFERENT STACKS
# IN OTHER HANDS => ITS NOT NECESSARY!
def merge_user_stacks(user):  # temporary approach
    try:
        # find all stacks belonging to the same user
        stacks_belonging_to_user = Cart.objects.filter(belongs_to=user)
        # stacks_belonging_to_user.sort(key=lambda x: x.created)  # sort by creation date ==> want to take the oldest one and delete others
        merged_stack = stacks_belonging_to_user[0]
        merged_stack_taken_products = TakenProduct.objects.filter(stack=merged_stack)

        if stacks_belonging_to_user and len(stacks_belonging_to_user) > 1:  # if umber of cart is one there's no need
            trash = []
            # removing stacks directly will change the size of the stacks_belonging_to_user, and causes trouble
            # so i save the un wanted stacks in 'trash' and after that delete the items of trash one by one
            for stack in stacks_belonging_to_user:
                if stack.ID() != merged_stack.ID():
                    if stack.owner is None and stack.worth == 0 and stack.discounts < 100:
                        trash.append(stack)
                    else:
                        products_taken_by_user = TakenProduct.objects.filter(stack=stack)
                        if products_taken_by_user:
                            for taken_product in products_taken_by_user:
                                taken_is_duplicate = False
                                # now check if there is a similar product with exact variation in the merged cart takens list
                                # if so just add the quantity of this one to the merged one and then delete this duplicate one
                                similar_products_in_merged_stack = merged_stack_taken_products.filter(product=taken_product.product)
                                for possibly_duplicate in similar_products_in_merged_stack:
                                    if possibly_duplicate.variation == taken_product.variation:
                                        possibly_duplicate.quantity += taken_product.quantity
                                        possibly_duplicate.save()
                                        taken_product.delete()
                                        taken_is_duplicate = True
                                        break

                                if not taken_is_duplicate:
                                    taken_product.cart = merged_stack
                                    taken_product.save()

                        trash.append(stack)
            for stack in trash:
                stack.delete()

            # remove empty stacks:
            Cart.objects.filter(belongs_to=None, cost=0).delete()
    except Exception as ex:
        print('sth went wrong while trying to merge stacks: ' + ex.__str__())
