from .models import Cart, TakenProduct
from .utlities import open_stack


def stack_counter(request):
    count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            stack = open_stack(request)

            if request.author.is_authenticated:
                items = TakenProduct.objects.all().filter(stack__belongs_to=request.author)
            else:
                items = TakenProduct.objects.all().filter(stack=stack)

            count = len(items)
        except:
            count = 0

    return dict(stack_counter=count)
