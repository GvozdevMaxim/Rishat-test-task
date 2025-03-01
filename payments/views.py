from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import View
from rishat import settings
from .models import Item, Order
from django.http.response import JsonResponse
import stripe

from .utils import get_currency_symbol

domain = settings.DEV_DOMAIN if settings.DEBUG else settings.PROD_DOMAIN


class CheckoutSessionView(View):
    """API View для создания Stripe-Checkout-Session"""

    def get(self, request, pk, *args, **kwargs):

        item = get_object_or_404(Item, pk=pk)
        if item.currency == 'GBP':
            stripe.api_key = settings.STRIPE_SECRET_KEY_GBP
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY_USD
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": item.currency,
                            "product_data": {
                                "name": item.name,
                                "description": item.description,
                            },
                            "unit_amount": int(item.price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{domain}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain}/cancel"
            )
            return JsonResponse({"session_id": session.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class ProductView(DetailView):
    model = Item
    template_name = "payments/product.html"
    context_object_name = 'item'


class OrderPaymentIntentView(View):
    """Создает Stripe PaymentIntent для оплаты заказа с учетом скидок и налогов"""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, id=pk)
        items = order.all_items.all()

        if not items.exists():
            return JsonResponse({"error": "Order has no items"}, status=400)

        # Определяем ключ Stripe
        currency = items[0].currency
        if currency == 'GBP':
            stripe.api_key = settings.STRIPE_SECRET_KEY_GBP
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY_USD

        # Проверяем, что все товары в одной валюте
        if any(item.currency != currency for item in items):
            return JsonResponse({"error": "All items must have the same currency"}, status=400)

        # Подсчет стоимости товаров
        subtotal_amount = sum(item.price for item in items)

        # Подсчет скидок
        total_discount = sum(discount.percentage for discount in order.discounts.all())
        discount_amount = int(subtotal_amount * (total_discount / 100))

        # Подсчет налогов
        total_tax = sum(tax.percentage for tax in order.taxes.all())
        tax_amount = int((subtotal_amount - discount_amount) * (total_tax / 100))

        total_amount = subtotal_amount - discount_amount + tax_amount

        if total_amount <= 0:
            return JsonResponse({"error": "Order total must be greater than zero"}, status=400)

        try:
            intent = stripe.PaymentIntent.create(
                amount=total_amount * 100,
                currency=currency.lower(),
                description=f"Order #{order.id}",
                metadata={"order_id": order.id}
            )

            return JsonResponse({"client_secret": intent.client_secret})

        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=500)


class OrderView(DetailView):
    model = Order
    template_name = "payments/order.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        items = order.all_items.all()

        subtotal = sum(item.price for item in items)
        discount = subtotal * sum(d.percentage for d in order.discounts.all()) / 100


        tax_percentage = sum(tax.percentage for tax in order.taxes.all()) if order.taxes.exists() else 0
        tax = (subtotal - discount) * (tax_percentage / 100)

        total = subtotal - discount + tax

        context["items"] = items
        context["subtotal_price"] = round(subtotal, 2)
        context["discount_amount"] = round(discount, 2)
        context["tax_percentage"] = round(tax_percentage, 2)
        context["tax_amount"] = round(tax, 2)
        context["total_price"] = round(total, 2)
        context["currency_symbol"] = get_currency_symbol(items[0].currency)



        return context


class SuccessView(TemplateView):
    template_name = "payments/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.request.GET.get('session_id')
        if session_id:
            context["session_id"] = session_id
        return context


class CancelView(TemplateView):
    template_name = "payments/cancel.html"
