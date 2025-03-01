from django.contrib import admin
from django.core.exceptions import ValidationError
from .forms import OrderForm
from .models import Order, Item, Discount, Tax
from .utils import get_currency_symbol


class DiscountInline(admin.TabularInline):
    model = Order.discounts.through
    extra = 1
    verbose_name = "Discount"
    verbose_name_plural = "Discounts"


class TaxInline(admin.TabularInline):
    model = Order.taxes.through
    extra = 1
    verbose_name = "Tax"
    verbose_name_plural = "Taxes"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ("id", "total_price_display", "items_list", "discounts_list", "taxes_list")
    search_fields = ("id",)

    filter_horizontal = ("all_items",)

    def save_related(self, request, obj, form, formsets):
        super().save_related(request, obj, form, formsets)
        items = obj.all_items.all()

        if not items.exists():
            raise ValidationError("Нельзя создать заказ без товаров.")

        currencies = items.values_list("currency", flat=True).distinct()
        if len(currencies) > 1:
            raise ValidationError("Все товары в заказе должны быть в одной валюте.")

    def total_price_display(self, obj):
        total, currency = obj.total_price()
        currency_symbol = "$" if currency == "usd" else "£"
        return f"{currency_symbol}{total:,.2f}" if currency_symbol else f"{total:,.2f} {currency or ''}"

    total_price_display.short_description = "Total Price"

    def items_list(self, obj):
        items = obj.all_items.all()
        if items.exists():
            return ", ".join([
                f"{item.name} - {get_currency_symbol(item.currency)}{item.price:,.2f}"
                for item in items
            ])
        return "—"

    items_list.short_description = "Items"

    def discounts_list(self, obj):
        discounts = obj.discounts.all()
        if discounts.exists():
            return ", ".join([
                f"{discount.name} - {discount.percentage}%"
                for discount in discounts
            ])
        return "—"

    discounts_list.short_description = "Discounts"

    def taxes_list(self, obj):
        taxes = obj.taxes.all()
        if taxes.exists():
            return ", ".join([
                f"{tax.name} - {tax.percentage}%"
                for tax in taxes
            ])
        return "—"

    taxes_list.short_description = "Taxes"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Админка для товаров."""
    list_display = ("name", "price", "currency")
    search_fields = ("name",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Админка для скидок."""
    list_display = ("name", "percentage")
    search_fields = ("name",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """Админка для налогов."""
    list_display = ("name", "percentage")
    search_fields = ("name",)
