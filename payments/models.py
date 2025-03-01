from django.db import models

CURR_CHOICES = (('usd', 'USD'), ('gbp', 'GBP'))


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    currency = models.CharField(choices=CURR_CHOICES, default='USD')

    objects = models.Manager()

    def __str__(self):
        return self.name


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.FloatField(default=0.0, help_text="Скидка в процентах)")

    def __str__(self):
        return f"Discount: {self.name} ({self.percentage}%)"


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.FloatField(default=0.0, help_text="Налог в процентах")

    def __str__(self):
        return f"Tax: {self.name} ({self.percentage}%)"


class Order(models.Model):
    all_items = models.ManyToManyField(Item, related_name='orders')
    discounts = models.ManyToManyField(Discount, blank=True, related_name="orders")
    taxes = models.ManyToManyField(Tax, blank=True, related_name="orders")

    def total_price(self):
        items = self.all_items.all()

        currency = items.first().currency
        item_total = sum(item.price for item in items)
        discount_percentage = sum(discount.percentage for discount in self.discounts.all()) / 100
        tax_percentage = sum(tax.percentage for tax in self.taxes.all()) / 100

        total = item_total * (1 - discount_percentage) * (1 + tax_percentage)
        return round(total, 2), currency
