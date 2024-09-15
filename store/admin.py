from django.contrib import admin
from .models import Product, Variation, Review, Gallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class GalleryInlinePanel(admin.TabularInline):
    model = Gallery
    extra = 1


class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'category', 'restaurant', 'is_available',)
    list_editable = ('is_available', )
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('category', 'is_available', 'restaurant', 'discount', )
    readonly_fields = ('created_at', 'updated_at', )
    search_fields = ('name', 'name_fa', 'category', 'content', 'restaurant__name', 'restaurant__name_fa', 'price', 'created_at',)
    inlines = (GalleryInlinePanel, )


# ،TODO: add inline variations below product panel
class VariationAdminPanel(admin.ModelAdmin):
    list_display = ('product', 'restaurant_name', 'size', 'color',)
    list_editable = ('is_available', 'stock',)
    list_filter = ('is_available', 'size', 'color', 'stock', )
    search_fields = ('size', 'color', 'product__name', 'product__name_fa')
    readonly_fields = ('created_at', 'updated_at', )


admin.site.register(Product, ProductAdminPanel)
admin.site.register(Variation, VariationAdminPanel)
admin.site.register(Review)  # TODO: Customize Review Panel
admin.site.register(Gallery) # TODO: Customize Gallery Panel

