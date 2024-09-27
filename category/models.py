from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save


# category model for classifying your products
class Category(models.Model):
    name = models.CharField(max_length=256, blank=False, unique=True, verbose_name="نام (انگلیسی)")
    name_fa = models.CharField(max_length=256, blank=False, unique=True, verbose_name="نام")
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField(max_length=512, blank=True, verbose_name="توضیحات")
    icon = models.ImageField(upload_to='photos/categories/', blank=True, verbose_name="آیکون")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی شده")

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    def url(self):
        return reverse('filtered_by_category', args=[self.slug])  # or-> '/store/' + self.slug + '/'

    def __str__(self) -> str:
        # define a language field in whole app, then decide to return .name or .name_fa
        # return self.name
        return self.name_fa


@receiver(pre_save, sender=Category)
def prepopulate_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify({instance.name})
