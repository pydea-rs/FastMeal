# Generated by Django 3.2.12 on 2022-10-20 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='bought',
        ),
    ]
