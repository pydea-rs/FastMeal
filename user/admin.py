from django.contrib import admin
from .models import User, Profile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


class UserAdminPanel(UserAdmin):
    list_display = ('phone', 'fname', 'lname', 'email', 'joining_date', 'last_login', 'is_activated')
    list_display_links = ('phone', 'email')
    readonly_fields = ('id', 'joining_date', 'last_login')
    ordering = ('-joining_date', )  # sort list by joining_date descending order
    filter_horizontal = ()
    search_fields = ('phone', 'fname', 'lname', 'email', )
    list_filter = ('is_activated', 'is_superuser',)
    fieldsets = (('مسائل ناموسی', {'fields': ('phone', 'password', 'id')}),
                 ('اصل', {'fields': ('fname', 'lname', 'email', 'joining_date')}),
                 ('دسترسی ها', {'fields': ('is_superuser', 'is_staff', 'is_activated')}),)

    add_fieldsets = (('مسائل ناموسی', {'fields': ('phone', 'password')}),
                     ('اصل', {'fields': ('fname', 'lname', 'email', 'joining_date')}),
                     ('دسترسی ها', {'fields': ('is_staff', 'is_superuser', )}),)


class ProfilePanel(admin.ModelAdmin):
    def avatar_thumbnail(self, obj):
        return format_html('<img src="{}" width="48" height="48" style="border-radius: 50%;" />'.format(obj.avatar.url if obj.avatar else "/static/images/noavatar.jpeg"))
    avatar_thumbnail.short_description = 'Avatar'
    list_display = ('avatar_thumbnail', 'user', 'province', 'city')


admin.site.register(User, UserAdminPanel)
admin.site.register(Profile, ProfilePanel)
