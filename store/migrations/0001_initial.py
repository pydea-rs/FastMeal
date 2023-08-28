# Generated by Django 3.2.9 on 2023-08-28 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='آیدی')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='نام به اجنبی')),
                ('name_fa', models.CharField(max_length=64, unique=True, verbose_name='نام')),
                ('slug', models.SlugField(max_length=64, unique=True, verbose_name='اسلاگ')),
                ('description', models.TextField(blank=True, max_length=1024, verbose_name='مشخصات')),
                ('price', models.IntegerField(verbose_name='شیتیل')),
                ('available', models.BooleanField(default=True, verbose_name='در دسترس؟')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='تاریخ تغییر')),
                ('discount', models.IntegerField(default=0, verbose_name='تخفیف')),
                ('image', models.ImageField(upload_to='photos/products', verbose_name='تصویر')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category', verbose_name='دسته بندی')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.shop')),
            ],
            options={
                'verbose_name': 'کالا',
                'verbose_name_plural': 'کالا ها',
            },
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('size', models.CharField(max_length=10, verbose_name='سایز')),
                ('color', models.CharField(max_length=20, verbose_name='رنگ')),
                ('is_available', models.BooleanField(default=True, verbose_name='در دسترس؟')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('stock', models.IntegerField(default=0, verbose_name='موجودی')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product', verbose_name='کالای مرتبط')),
            ],
            options={
                'verbose_name': 'گونه',
                'verbose_name_plural': 'گونه ها',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, max_length=500, verbose_name='سخنوری')),
                ('rating', models.FloatField(verbose_name='امتیازدهی')),
                ('ip', models.CharField(blank=True, max_length=20)),
                ('status', models.BooleanField(default=True, verbose_name='وضعیت')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درافشانی')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='به روز رسانی نظز')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product', verbose_name='کالای مرتبط')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'فیلان بیسار',
                'verbose_name_plural': 'فیلان ها و بیسارها',
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/products', verbose_name='تصویر')),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='store.product', verbose_name='کالای مرتبط')),
            ],
            options={
                'verbose_name': 'گالری',
                'verbose_name_plural': 'گالری',
            },
        ),
    ]
