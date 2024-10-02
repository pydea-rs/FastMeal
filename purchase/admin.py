from django.contrib import admin
from .models import Transaction, Order, PurchasedItem, DeliveryInfo, Receipt
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from common.tools import MailingInterface


# TODO:ADD TRANSACTION & ORDER RECEIVER MANAGERS CLASSES AS INLINES FOR ORDER ADMIN PANEL
class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem
    readonly_fields = ('product', 'variation', 'order', 'buyer', 'quantity', 'cost', 'delivered')
    fields = ('product', 'variation', 'quantity', 'cost')
    extra = 0


class DeliveryInfoInline(admin.TabularInline):
    model = DeliveryInfo
    readonly_fields = ('user', 'location', 'phone', 'notes')
    extra = 0


class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('key', 'owner', 'status', 'created_at', 'seen',)
    list_editable = ('status',)
    list_filter = ('status', 'seen',)
    search_fields = ('key', 'receiver__fname', 'receiver__lname', 'owner__fname', 'owner__lname', 'status')
    list_per_page = 20
    inlines = (PurchasedItemInline,) 
    change_form_template = "personalization/order_admin_template.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        order = get_object_or_404(Order, id=object_id)
        order.seen = True
        order.save()
        return super().change_view(request=request, object_id=object_id, form_url='', extra_context=None)

    def response_change(self, request, obj):
        order: Order | None = None
        try:
            if "btn_verify_order" in request.POST:
                order = get_object_or_404(Order, id=obj.id, key=obj.key)
                if order.status != "verified" and order.status != 'sent' and order.status != "delivered":
                    order.status = "verified"
                    order.seen = True
                    order.whats_wrong = None
                    if not order.owner or not order.owner.email:
                        messages.error(request, "خریدار این سفارش و یا ایمیل وی مشخص نیست. احتمالا اطلاعات این کاربر "
                                                "دستکاری شده است و نیاز به بررسی دارد.")
                        return redirect(request.path)
                    order.save()
                    # send email with details to notify that the order is verified and will be prepared to send
                    ref_id = order.transaction.receipt.reference_id if order.transaction and order.transaction.receipt else None
                    MailingInterface.SendMessage(request, order.owner.email, "تایید سفارش", "order_verified",
                                                 {"name": order.owner.fname, "order_key": order.key,
                                                  "reference_id": ref_id})
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
        except Exception as ex:
            print(f"Something went wrong while verifying the order: {order.key}; ", ex)
            if order:
                order.save()
        return super().response_change(request, obj)


class PurchasedItemAdminPanel(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'variation', 'quantity', 'created_at')
    list_filter = ('delivered', 'product', 'variation')
    search_fields = (
        'product__name', 'product__name_fa', 'order__key', 'variation__name',
        'order__receiver__fname', 'order__receiver__lname', 'order__owner__fname', 'order__owner__lname',
    )
    list_per_page = 20


class DeliveryInfoAdminPanel(admin.ModelAdmin):
    list_display = ('user__fname', 'user__lname', 'phone',  'location')
    list_filter = ('location', )
    search_fields = ('phone',  'location', 'notes', 'name')
    list_per_page = 20


class TransactionInlinePanel(admin.TabularInline):
    model = Transaction
    extra = 0


class ReceiptAdminPanel(admin.ModelAdmin):
    inlines = (TransactionInlinePanel,)
    list_display = ('reference_id', 'order_key', 'amount', )
    search_fields = ('reference_id', 'order_key', 'amount')
    list_display_links = ('reference_id',)


class TransactionAdminPanel(admin.ModelAdmin):
    list_display = ('source', 'receipt', 'validation', 'created_at')
    list_display_links = ('source', 'receipt')
    list_filter = ('validation', 'source', 'method', )
    search_fields = ('receipt__reference_id', 'source__fname',
                     'source__lname', 'validation', 'created_at', 'method',)


admin.site.register(Receipt, ReceiptAdminPanel)
admin.site.register(Transaction, TransactionAdminPanel)
admin.site.register(Order, OrderAdminPanel)
admin.site.register(PurchasedItem, PurchasedItemAdminPanel)
admin.site.register(DeliveryInfo, DeliveryInfoAdminPanel)
