from payments.models import Order
from django import forms
from django.core.exceptions import ValidationError


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        items = cleaned_data.get("all_items")

        if not items or items.count() == 0:
            raise ValidationError("Нельзя создать заказ без товаров.")

        currencies = items.values_list("currency", flat=True).distinct()
        if len(currencies) > 1:
            raise ValidationError("Все товары в заказе должны быть в одной валюте.")

        return cleaned_data
