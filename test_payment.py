import os
import django
import sys

# Setup django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import razorpay
from django.conf import settings
from apps.payments.models import Transaction

try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    amount = 10
    amount_paisa = int(float(amount) * 100)
    
    order_data = {
        'amount': amount_paisa,
        'currency': 'INR',
        'payment_capture': '1'
    }
    
    print(f"Creating order with Key: {settings.RAZORPAY_KEY_ID}")
    order = client.order.create(data=order_data)
    print("Order created successfully:", order)
except Exception as e:
    print("Error creating order:", str(e))
