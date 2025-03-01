"""
URL configuration for rishat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from payments.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buy/<int:pk>/', CheckoutSessionView.as_view(), name='buy-item'),
    path('item/<int:pk>/', ProductView.as_view(), name='item-detail'),
    path('buyorder/<int:pk>/', OrderPaymentIntentView.as_view(), name='buy-order'),
    path('order/<int:pk>/', OrderView.as_view(), name='order-detail'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
]
