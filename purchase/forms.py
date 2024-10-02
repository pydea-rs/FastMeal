from django import forms
from .models import DeliveryInfo, Receipt


class OrderForm(forms.ModelForm):
    class Meta:
        model = DeliveryInfo
        fields = ['location', 'phone', 'notes']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)


class ReserveTransactionForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['amount', 'image', 'reference_id', 'order_key']

    def __init__(self, *args, **kwargs):
        super(ReserveTransactionForm, self).__init__(*args, **kwargs)

    def clean(self):
        # get sent form's data to start checking
        print("ReserveTransactionForm clean method called")
        cleaned_data = super(ReserveTransactionForm, self).clean()

        if cleaned_data.get('amount') <= 0:
            raise forms.ValidationError('مقدار تراکنش باید بزرگتر از صفر باشد!')
