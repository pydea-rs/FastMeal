import uuid
from store.models import Product, Variation
from django.db import models
from user.models import User


class Cart(models.Model):
    sid = models.CharField(max_length=50, blank=True, verbose_name="شناسه سبد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روزرسانی شده")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="به نام")
    worth = models.IntegerField(default=0, verbose_name="ارزش سبد")  # total value (total price)
    discounts = models.IntegerField(default=0, verbose_name="مجموع تخفیف ها")

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = ' سبدهای خرید'

    def final_cost(self):
        result = self.worth - self.discounts
        int_result = int(result)
        return int_result if result == int_result else self.worth - self.discounts

    def __str__(self):
        return f'سبد {self.worth} تومنی متعلق به {self.owner}'

    def ID(self):
        return self.sid

    def submit_bill(self):
        self.worth = self.discounts = 0
        try:
            # if stack_owner.is_authenticated:
            # taken items = TakenProduct.objects.all().filter(stack__belongs_to=stack_owner).filter(is_available=True)
            # else:
            #    taken items = TakenProduct.objects.all().filter(cart=self).filter(is_available=True)
            taken_items = TakenProduct.objects.filter(stack=self, is_available=True)
            # calculate costs:
            for item in taken_items:
                self.worth += item.total_absolute_price()
                self.discounts += item.total_discount()

            self.save()
        except TakenProduct.DoesNotExist:
            return {
                'cart': self,
                'taken_products': []
            }

        return {
            'cart': self,
            'taken_products': taken_items
        }


class TakenProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, verbose_name="نوع")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="سبد")
    quantity = models.IntegerField(default=0, verbose_name="تعداد")
    is_available = models.BooleanField(default=True, verbose_name="در دسترس؟")  # TODO: Remove this field
    added_to_cart_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ قرار گرفتن در سبد")

    class Meta:
        verbose_name = 'آیتم داخل سبد'
        verbose_name_plural = 'آیتم های داخل سبد'

    def increment_quantity(self):
        if self.product.is_available and self.variation.is_available:
            self.quantity += 1

    def decrement_quantity(self):
        self.quantity = self.quantity - 1 if self.quantity > 0 else 0

    def ID(self):
        return self.id

    def total_absolute_price(self):  # the price of all items of this product(and variation) without considering
        # discounts
        return self.quantity * self.variation.price

    def sell_price(self):  # each item price considering the discounts
        return int(self.variation.price * (100 - self.product.discount) / 100)

    def final_price(self):  # absolute price considering the quantity of the item and discounts
        return self.sell_price() * self.quantity

    def total_discount(self):
        result = self.total_absolute_price() * self.product.discount / 100
        int_result = int(result)
        return int_result if int_result == result else result

    def __str__(self):
        return '%s [%d]' % (self.product.__str__(), self.quantity)

    def __unicode__(self):
        return self.product

    @property
    def has_min_quantity(self):
        return self.quantity > 1