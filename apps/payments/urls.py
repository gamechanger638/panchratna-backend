from django.urls import path
from .views import CreateOrderView, VerifyPaymentView

urlpatterns = [
    path('payments/create-order/', CreateOrderView.as_view(), name='create-order'),
    path('payments/verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
]
