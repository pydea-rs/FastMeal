from os.path import join
from django.db import models
from category.models import Category
from django.urls import reverse
import uuid
from user.models import User
from django.db.models import Avg, Count
from restaurant.models import Restaurant


class Product(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=False, verbose_name="نام (انگلیسی)")
    name_fa = models.CharField(max_length=128, unique=True, blank=False, verbose_name="نام (فارسی)")
    slug = models.SlugField(max_length=128, unique=True, verbose_name="نام صفحه (خودکار)")
    content = models.TextField(max_length=256, blank=True, verbose_name="محتویات")
    price = models.IntegerField(verbose_name="قیمت پایه")
    is_available = models.BooleanField(default=True, verbose_name="در دسترس بودن")
    discount = models.IntegerField(default=0, verbose_name="تخفیف")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name="دسته بندی")
    image = models.ImageField(upload_to='photos/food', verbose_name="تصویر")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد مشخصات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی مشخصات")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def url(self):
        return reverse('single_product', args=[self.category.slug, self.slug])

    def ID(self):
        return self.id

    def __str__(self):
        return self.name_fa
        # return self.name_fa

    def format_rating(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(average_rating=Avg('rating'),
                                                                             count=Count('id'))
        if reviews['count']:
            return f'{float(reviews["average_rating"])}/5.0 [{int(reviews["count"])}]'
        return "-"

    def rating(self):
        try:
            return Review.objects.filter(product=self, status=True).aggregate(average_rating=Avg('rating'))[
                'average_rating']
        except Exception as ex:
            print("Something went wrong while calculating product rating because: ", ex)
        return None


class VariationManager(models.Manager):
    class Meta:
        verbose_name = "سازمان دهنده مشخصات"
        verbose_name_plural = "سازمان دهنده مشخصات"

    def get_product_variations(self):
        variations = super(VariationManager, self).filter(is_available=True)
        return variations

    def find_specific_variation(self, variation_name):
        return super(VariationManager, self).filter(name=variation_name, is_available=True)

    def displayable(self):
        return super(VariationManager, self).all().count() > 0

    def item_exists(self, variation_name: str):
        return super(VariationManager, self).filter(name=variation_name).count() > 0

    def variation_count(self, variation: str):
        return super(VariationManager, self).filter(name=variation,is_available=True).count()


class Variation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "نوع محصول"
        verbose_name_plural = "انواع محصول"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    # parameter means that on what parameter this variation differs from other variations with same Product
    name = models.CharField(max_length=64, verbose_name="نام نوع")

    is_available = models.BooleanField(default=True, verbose_name="در دسترس بودن")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی مشخصات")
    objects = VariationManager()
    price = models.IntegerField(verbose_name="قیمت")

    def restaurant_name(self):
        return self.product.restaurant.name_fa

    def ID(self):
        return self.id

    def __str__(self):
        return f'{self.name}'


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name="کالای مرتبط")
    image = models.ImageField(upload_to='photos/products', verbose_name="تصویر")

    class Meta:
        verbose_name = "گالری"
        verbose_name_plural = "گالری"

    def __str__(self):
        return self.product.__str__()


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالای مرتبط")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده")
    comment = models.TextField(max_length=1024, blank=True, verbose_name="کامنت")
    rating = models.FloatField(verbose_name="امتیاز")
    ip = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=True, verbose_name="وضعیت تایید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال نظر")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی نظز")

    class Meta:
        verbose_name = 'فیلان بیسار'
        verbose_name_plural = 'فیلان ها و بیسارها'

    def __str__(self):
        return f'{self.author.fname}: {self.comment}'
