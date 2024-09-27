from django.contrib import admin
from .models import Category


class CategoryAdminPanel(admin.ModelAdmin):
    list_display = ['name_fa', 'name']
    search_fields = ('name', 'name_fa', )
    readonly_fields = ('created_at', 'updated_at', 'slug')


admin.site.register(Category, CategoryAdminPanel)
