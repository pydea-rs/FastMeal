from django.db import models
from category.models import Category
from django.urls import reverse
from user.models import User
from django.db.models import Avg, Count
from restaurant.models import Restaurant
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save


class Product(models.Model):
    name = models.CharField(max_length=256, blank=False, verbose_name="نام (انگلیسی)")
    name_fa = models.CharField(max_length=256, blank=False, verbose_name="نام")
    slug = models.SlugField(max_length=600, unique=True)
    is_available = models.BooleanField(default=True, verbose_name="در دسترس بودن")
    discount = models.IntegerField(default=0, verbose_name="تخفیف")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name="دسته بندی")
    image = models.ImageField(upload_to='photos/food', verbose_name="تصویر")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING, blank=False,
                                   null=False, verbose_name='رستوران')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد مشخصات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی مشخصات")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    @property
    def price(self):
        variations = self.variation_set.all
        if not variations:
            return None
        min_price = min(variations, key=lambda var: var.price).price
        max_price = max(variations, key=lambda var: var.price).price
        return min_price if min_price == max_price else f'{min_price} - {max_price}'

    @property
    def url(self):
        return reverse('single_product', args=[self.category.slug, self.slug])

    @property
    def ID(self):
        return self.id

    def __str__(self):
        return self.name_fa
        # return self.name_fa

    @property
    def format_rating(self):
        rating = self.rating
        if rating:
            return f'{float(rating)}/5.0'
        return "-"

    @property
    def reviews_count(self):
        return Review.objects.filter(product=self, verified=True).count()

    @property
    def rating(self):
        try:
            return Review.objects.filter(product=self, verified=True).aggregate(average_rating=Avg('rating'))[
                'average_rating']
        except Exception as ex:
            print("Something went wrong while calculating product rating because: ", ex)
        return None


class VariationManager(models.Manager):
    class Meta:
        verbose_name = "سازمان دهنده مشخصات"
        verbose_name_plural = "سازمان دهنده مشخصات"

    @property
    def all(self):
        return super(VariationManager, self).filter(is_available=True)

    def find_specific_variation(self, variation_name):
        return super(VariationManager, self).filter(name=variation_name, is_available=True)

    @property
    def displayable(self):
        return super(VariationManager, self).filter(is_available=True).count() > 0

    def item_exists(self, variation_name: str):
        return super(VariationManager, self).filter(name=variation_name).count() > 0

    @property
    def count(self):
        return super(VariationManager, self).filter(is_available=True).count()

    @property
    def specifics(self):
        variations = super(VariationManager, self).filter(is_available=True)
        result = {}
        for var in variations:
            result[var.id] = {'price': var.price, 'content': var.content}
        return result


class Variation(models.Model):
    class Meta:
        verbose_name = "نوع محصول"
        verbose_name_plural = "انواع محصول"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    # parameter means that on what parameter this variation differs from other variations with same Product
    name = models.CharField(max_length=64, verbose_name="نام نوع")

    is_available = models.BooleanField(default=True, verbose_name="در دسترس بودن")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی مشخصات")
    price = models.IntegerField(verbose_name="قیمت")
    content = models.TextField(max_length=256, blank=True, verbose_name="محتویات")
    objects = VariationManager()

    @property
    def restaurant_name(self):
        return self.product.restaurant.name_fa

    @property
    def product_name(self):
        return self.product.name_fa

    @property
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
        verbose_name = 'نظر کاربر'
        verbose_name_plural = 'نظرات کاربران'

    def __str__(self):
        return f'{self.author.fname}: {self.comment}'


# Special functions
@receiver(pre_save, sender=Product)
def prepopulate_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug = slugify(f"{instance.name}-{instance.restaurant.slug}")
        existing = Product.objects.filter(slug__icontains=slug).count()
        instance.slug = slug if not existing else f'{slug}-{existing + 1}'
