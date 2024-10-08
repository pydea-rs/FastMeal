from django.contrib import admin
from .models import DevShare


# Register your models here.


class DevShareAdminPanel(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status',)
    list_filter = ('status',)

    readonly_fields = ('status', 'order', 'amount', 'created_at', 'updated_at')
    search_fields = ('order__receiver__fname', 'order__receiver__lname', \
                     'order__owner__fname', 'order__owner__lname', 'order__key', 'status', 'amount')

    # inlines = (TakenProductInline, )

    def has_delete_permission(self, request, obj=None):
        return False


# admin.site.register(DevShare, DevShareAdminPanel)
