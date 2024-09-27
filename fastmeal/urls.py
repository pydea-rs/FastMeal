from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='honey_admin')),
    path('panel/', admin.site.urls, name='real_admin'),
    path('', views.home, name="home"),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('purchase/', include('purchase.urls')),
    path('user/', include('user.urls')),
    # path('gateways/', include('gateways.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('search/', views.search, name='search'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]