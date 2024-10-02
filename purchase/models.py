from django.db import models
import datetime
from store.models import Variation, Product
from user.models import User
from django.urls import reverse

ORDER_STATUS = {
    'new': 'جدید',
    'pending': 'در دست بررسی',
    'verified': 'تایید شده',
    'sent': ' ارسال شده',
    'delivered': 'تحویل شده',
    'refused': 'عدم تایید',
    'not_available': 'عدم موجودی',
    'sending_error': 'مشکل در ارسال',
    'delivery_error': ' مشکل در تحویل',
    'canceled': 'ناموفق'
}


class Receipt(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='پرداخت کننده', )
    reference_id = models.CharField(max_length=30, verbose_name='کد رهیگیری')  # *** WHAT TO SET ON MAX_LENGTH ??
    image = models.ImageField(upload_to='photos/transactions', blank=True, null=True, verbose_name='عکس رسید')
    amount = models.IntegerField(verbose_name="مقدار تراکنش")
    order_key = models.CharField(max_length=20, verbose_name='شماره سفارش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد', )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روزرسانی',)

    class Meta:
        verbose_name = 'رسید'
        verbose_name_plural = 'رسیدها'

    def __str__(self):
        return self.reference_id


class Transaction(models.Model):
    METHODS = (('reserve', 'رزرو'),
              ('zarinpal', 'زرین پال'),
              ('bank_portal', 'درگاه پرداخت بانکی'))
    VALIDATION_STATUS = (('pending', 'در دست بررسی'), ('valid', 'معتبر'), ('invalid', 'نامعتبر'))
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, blank=True, null=True, verbose_name='رسید')
    validation = models.CharField(max_length=20, choices=VALIDATION_STATUS,
                                  default='pending', verbose_name='صحت تراکنش')
    source = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='پرداخت کننده')
    method = models.CharField(max_length=20, blank=False, choices=METHODS, verbose_name='روش پرداخت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روزرسانی')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'

    def __str__(self):
        return self.receipt.__str__() if self.receipt.__str__() else "Uncertified"


class DeliveryInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر مربوطه')
    location = models.CharField(max_length=256, verbose_name="محل تحویل", blank=False)
    phone = models.CharField(max_length=11, verbose_name='شماره تماس دوم', blank=True)
    notes = models.CharField(max_length=512, verbose_name="ملاحضات", blank=True, null=True, default=None)

    class Meta:
        verbose_name = 'اطلاعات تحویل گیرنده'
        verbose_name_plural = 'اطلاعات تحویل گیرنده'

    def __str__(self):
        return self.location.__str__()

    @property    
    def name(self):
        return self.user.__str__()


class Order(models.Model):
    # order possible status

    STATUS = (('new', ORDER_STATUS['new']), # FIXME: Arrange all these status, only use some
              ('pending', ORDER_STATUS['pending']),
              ('verified', ORDER_STATUS['verified']),
              ('sent', ORDER_STATUS['sent']),
              ('delivered', ORDER_STATUS['delivered']),
              ('separator', '--------------------'),
              ('refused', ORDER_STATUS['refused']),
              ('not_available', ORDER_STATUS['not_available']),
              ('sending_error', ORDER_STATUS['sending_error']),
              ('delivery_error', ORDER_STATUS['delivery_error']),
              ('canceled', ORDER_STATUS['canceled']),)

    # EDIT ON_DELETE s
    key = models.CharField(max_length=20, verbose_name='شماره سفارش')
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name='صاحب سفارش')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تراکنش')

    receiver = models.ForeignKey(DeliveryInfo, on_delete=models.PROTECT, verbose_name='مشخصات گیرنده', default=None) 

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روزرسانی')
    status = models.CharField(max_length=20, choices=STATUS, default='new', verbose_name='وضعیت')

    cost = models.IntegerField(default=0, verbose_name='هزینه')
    discounts = models.IntegerField(default=0, verbose_name='مبلغ تخفیف')

    shipping_cost = models.IntegerField(default=0, verbose_name='هزینه ارسال')
    seen = models.BooleanField(default=False, verbose_name='مشاهده توسط ادمین')
    whats_wrong = models.TextField(max_length=256, null=True, blank=True, verbose_name='علت رد سفارش')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'

    @property
    def discounts_amount(self):
        return self.discounts if self.discounts else "-"

    @property
    def final_cost(self):
        return self.cost - self.discounts + self.shipping_cost

    def __str__(self):
        return 'سفارشی به نام' + self.receiver.name

    def check_url(self):
        return reverse('check_order', args=[self.key])

    def accept_url(self):
        return reverse('accept_order', args=[self.key])

    def receipt_url(self):
        return reverse('order_receipt', args=[self.key])

    def keygen(self):
        # now I generate the order key: the key that that identifies the order for both seller and buyer
        year = int(datetime.date.today().strftime('%Y'))
        month = int(datetime.date.today().strftime('%m'))
        day = int(datetime.date.today().strftime('%d'))
        today = datetime.date(year, month, day)  # construct today's date in proper format and object
        return today.strftime('%Y%m%d') + str(self.id)  # django default primary key: id starts from 1 increasing by one

    def status_fa(self):
        return ORDER_STATUS[str(self.status)]


class PurchasedItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='سفارش مربوطه')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='مالک زدوبند')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, verbose_name='نوع')
    quantity = models.IntegerField(default=0, verbose_name='تعداد')
    cost = models.IntegerField(verbose_name='هزینه')

    delivered = models.BooleanField(default=False, verbose_name='تحویل شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ به روزرسانی')

    class Meta:
        verbose_name = 'آیتم سفارشی'
        verbose_name_plural = 'آیتم های سفارشی'

    def __str__(self):
        return f'{self.product} - {self.variation} [{self.quantity}]'

    def ID(self):
        return self.id

    def total_price(self):  # the price of all items of this product(and variation) without considering discounts
        return self.quantity * self.variation.price

    def absolute_price(self):  # each item price considering the discounts
        return int(self.variation.price * (100 - self.product.discount) / 100)

    def final_price(self):  # absolute price considering the quantity of the item and discounts
        return self.absolute_price() * self.quantity

    def total_discount(self):
        return self.total_price() * self.product.discount / 100

    def __unicode__(self):
        return self.product
