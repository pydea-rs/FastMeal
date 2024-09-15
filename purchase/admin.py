from django.contrib import admin
from .models import Transaction, Order, PurchasedItem, OrderReceiver, Receipt
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from common.tools import MailingInterface
from devshare.models import DevShare


# TODO:ADD TRANSACTION & ORDER RECEIVER MANAGERS CLASSES AS INLINES FOR ORDER ADMIN PANEL
class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem

    readonly_fields = ('product', 'variation', 'order', 'buyer', 'quantity', 'cost', 'delivered')
    fields = ('product', 'variation', 'quantity', 'cost')
    extra = 0


class OrderReceiverInline(admin.TabularInline):
    model = OrderReceiver
    readonly_fields = ('user', 'fname', 'lname', 'province', 'city', 'phone', 'address', 'postal_code')
    extra = 0


class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('key', 'buyer', 'status', 'seen',)
    list_editable = ('status',)
    list_filter = ('status', 'seen',)
    search_fields = ('key', 'receiver__fname', 'receiver__lname', 'owner__fname', 'owner__lname', 'status')
    list_per_page = 20
    inlines = (PurchasedItemInline,)  # OrderReceiverInline)
    change_form_template = "personalization/order_admin_template.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        order = get_object_or_404(Order, id=object_id)
        order.seen = True
        order.save()
        return super().change_view(request=request, object_id=object_id, form_url='', extra_context=None)

    def response_change(self, request, obj):
        try:
            if "btn_verify_order" in request.POST:
                order = get_object_or_404(Order, id=obj.id, key=obj.key)
                if order.status != "verified" and order.status != 'sent' and order.status != "delivered":
                    order.status = "verified"
                    order.seen = True
                    goods = PurchasedItem.objects.filter(order=order)

                    for item in goods:
                        item.variation.stock -= item.quantity
                        item.variation.save()
                        item.save()

                    order.whats_wrong = None
                    # send email with details to notify that the order is verified and will be prepared to send
                    if not order.owner or not order.owner.email:
                        messages.error(request, "خریدار این سفارش و یا ایمیل وی مشخص نیست. احتمالا اطلاعات این کاربر "
                                                "دستکاری شده است و نیاز به بررسی دارد.")
                        return redirect(request.path)
                    ref_id = order.transaction.receipt.reference_id if order.transaction and order.transaction.receipt else None
                    MailingInterface.SendMessage(request, order.owner.email, "تایید سفارش", "order_verified",
                                                 {"name": order.owner.fname, "order_key": order.key,
                                                  "reference_id": ref_id})
                    order.save()
                    try:
                        dev_share = DevShare.objects.get(order=order)
                        dev_share.verify()
                        dev_share.save()
                    except Exception as ex:
                        print("Cannot retrieve developer share: ", ex)
                else:
                    messages.info(request, "این سفارش قبلا تایید شده است.")
                    return redirect(request.path)
            elif "btn_cancel_order" in request.POST:
                cause = request.POST["whats_wrong"]
                if not cause:
                    messages.error(request, "علت رد سفارش را وارد کن.")
                    return redirect(request.path)

                order = get_object_or_404(Order, id=obj.id, key=obj.key)
                order.whats_wrong = cause
                order.seen = True
                order.save()
                if not order.owner or not order.owner.email:
                    messages.error(request,
                                   "خریدار این سفارش و یا ایمیل وی مشخص نیست. احتمالا اطلاعات این کاربر دستکاری شده "
                                   "است و نیاز به بررسی دارد.")
                    return redirect(request.path)

                MailingInterface.SendMessage(request,
                                             target_email=order.owner.email,
                                             subject="سفارش نامعتبر",
                                             template_name="order_refused",
                                             dict_content={"name": order.owner.fname,
                                                           "order_key": order.key,
                                                           "whats_wrong": cause})
                # send email to notify
                # change order status
                # or remove the order?
            elif "btn_indebt" in request.POST:
                pass
            #  COMPLETE THIS IF
        except Exception as ex:
            print("Something went wrong while verifying the order: ", ex)
        return super().response_change(request, obj)


class PurchasedItemAdminPanel(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'variation', 'quantity',)
    list_filter = ('delivered',)
    search_fields = (
        'product__name', 'product__name_fa', 'order__key', 'variation__name',
        'order__receiver__fname', 'order__receiver__lname', 'order__owner__fname', 'order__owner__lname',
    )
    list_per_page = 20


class OrderReceiverAdminPanel(admin.ModelAdmin):
    list_display = ('phone', 'fname', 'lname', 'province', 'city')
    list_filter = ('province', 'city')
    search_fields = ('phone', 'fname', 'lname', 'province', 'city', 'postal_code', 'address')
    list_per_page = 20


class TransactionInlinePanel(admin.TabularInline):
    model = Transaction
    extra = 0


class ReceiptAdminPanel(admin.ModelAdmin):
    inlines = (TransactionInlinePanel,)
    list_display = ('reference_id', 'order_key', 'amount')
    search_fields = ('reference_id', 'order_key', 'amount')
    list_display_links = ('reference_id',)


class TransactionAdminPanel(admin.ModelAdmin):
    list_display = ('receipt', 'validation', 'source', 'created_at')
    list_filter = ('validation', 'method',)
    search_fields = ('receipt__reference_id', 'source__fname',
                     'source__lname', 'validation', 'created_at', 'method',)


admin.site.register(Receipt, ReceiptAdminPanel)
admin.site.register(Transaction, TransactionAdminPanel)
admin.site.register(Order, OrderAdminPanel)
admin.site.register(PurchasedItem, PurchasedItemAdminPanel)
admin.site.register(OrderReceiver, OrderReceiverAdminPanel)
