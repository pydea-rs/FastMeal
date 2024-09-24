from django.db import models
from user.models import User


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, verbose_name='مالک')
    name = models.CharField(max_length=128, blank=False, null=False, verbose_name='نام (انگلیسی)')
    name_fa = models.CharField(max_length=128, blank=False, null=False, verbose_name='نام (فارسی)')

    description = models.CharField(max_length=1024, blank=True, verbose_name='توضیحات')
    location = models.CharField(max_length=128, blank=False, null=False, verbose_name='آدرس')
    slug = models.SlugField(max_length=64, unique=True, verbose_name='اسلاگ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد مشخصات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی مشخصات")

    def __str__(self):
        return self.name_fa

    def rating(self):
        pass  # TODO: Calculate this

    class Meta:
        verbose_name = 'رستوران'
        verbose_name_plural = 'رستوران ها'


class RestaurantGallery(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default=None, verbose_name='رستوران')
    image = models.ImageField(upload_to='photos/shops', verbose_name="عکس")

    class Meta:
        verbose_name = "گالری رستوران"
        verbose_name_plural = "گالری رستوران ها"

    def __str__(self):
        return self.restaurant.name_fa
