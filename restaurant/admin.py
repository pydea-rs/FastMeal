from django.contrib import admin
from .models import Restaurant, RestaurantGallery


class RestaurantGalleryInlinePanel(admin.TabularInline):
    model = RestaurantGallery
    extra = 1


class RestaurantAdminPanel(admin.ModelAdmin):
    list_display = ('name_fa', 'owner')
    list_filter = ('owner', )
    search_fields = ('name', 'name_fa', 'owner', 'location')
    inlines = (RestaurantGalleryInlinePanel,)


# Register your models here.
admin.site.register(Restaurant, RestaurantAdminPanel)
admin.site.register(RestaurantGallery)