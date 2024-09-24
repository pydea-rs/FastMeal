from django.contrib import admin
from .models import Cart, TakenProduct


class TakenProductAdminPanel(admin.ModelAdmin):
    list_display = ('product',  'variation', 'cart', 'quantity', 'is_available', )
    list_filter = ('is_available', 'variation', 'cart', 'quantity', )
    search_fields = ('product__name', 'product__name_fa', 'variation__name', 
                     'cart__sid', 'cart__owner__fname', 'cart__owner__lname',)
    list_editable = ('is_available', )
    readonly_fields = ('added_to_cart_at',)


class TakenProductInline(admin.TabularInline):
    model = TakenProduct
    extra = 0


class CartAdminPanel(admin.ModelAdmin):
    list_display = ('sid', 'owner', 'worth', 'created_at')
    readonly_fields = ('sid', 'created_at', 'updated_at')
    search_fields = ('sid', 'owner__fname', 'owner__lname', 'cost')
    inlines = (TakenProductInline, )


admin.site.register(Cart, CartAdminPanel)
admin.site.register(TakenProduct, TakenProductAdminPanel)
