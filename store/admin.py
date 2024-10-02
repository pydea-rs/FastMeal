from django.contrib import admin
from .models import Product, Variation, Review, Gallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class GalleryInlinePanel(admin.TabularInline):
    model = Gallery
    extra = 1


class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name_fa', 'category', 'restaurant', 'price')  # TODO: Remove price if throws
    list_filter = ('category', 'restaurant', 'discount',)
    readonly_fields = ('created_at', 'updated_at', 'slug')
    search_fields = (
        'name', 'name_fa', 'category', 'content', 'restaurant__name', 'restaurant__name_fa',
    )
    inlines = (GalleryInlinePanel,)


# ،TODO: add inline variations below product panel
class VariationAdminPanel(admin.ModelAdmin):
    list_display = ('product_name', 'name', 'restaurant_name', 'price', 'is_available')
    list_editable = ('is_available', 'price',)
    list_filter = ('is_available', 'name', )
    search_fields = ('name', 'product__name', 'product__name_fa')
    readonly_fields = ('created_at', 'updated_at',)


admin.site.register(Product, ProductAdminPanel)
admin.site.register(Variation, VariationAdminPanel)
admin.site.register(Review)  # TODO: Customize Review Panel
admin.site.register(Gallery)  # TODO: Customize Gallery Panel
