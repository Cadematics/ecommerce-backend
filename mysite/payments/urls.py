from django.urls import path
from .views import StripePaymentIntentCreateView, StripeConfirmView

app_name = 'payments'

urlpatterns = [
    path(
        'stripe/create-intent/',
        StripePaymentIntentCreateView.as_view(),
        name='stripe-create-intent'
    ),
    path(
        'stripe/confirm/',
        StripeConfirmView.as_view(),
        name='stripe-confirm'
    ),
]
