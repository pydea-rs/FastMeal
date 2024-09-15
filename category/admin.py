from django.contrib import admin
from .models import Category


class CategoryAdminPanel(admin.ModelAdmin):
    list_display = ['name_fa', 'name']
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', 'name_fa', )
    readonly_fields = ('created_at', 'updated_at',)


admin.site.register(Category, CategoryAdminPanel)
