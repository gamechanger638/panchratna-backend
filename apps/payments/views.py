import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Transaction
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderView(APIView):
    permission_classes = [AllowAny] # Anyone can donate or pay small amount

    def post(self, request):
        try:
            amount = request.data.get('amount') # in Rupees
            if not amount:
                return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Amount for Razorpay is in Paisa (1 Rupee = 100 Paisa)
            amount_paisa = int(float(amount) * 100)
            
            order_data = {
                'amount': amount_paisa,
                'currency': 'INR',
                'payment_capture': '1' # Auto-capture
            }
            
            order = client.order.create(data=order_data)
            
            # Save transaction as pending
            Transaction.objects.create(
                user = request.user if request.user.is_authenticated else None,
                amount=amount,
                razorpay_order_id=order['id'],
                status='pending'
            )
            
            return Response(order, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_signature = request.data.get('razorpay_signature')
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Update transaction
            try:
                tx = Transaction.objects.get(razorpay_order_id=razorpay_order_id)
                tx.razorpay_payment_id = razorpay_payment_id
                tx.razorpay_signature = razorpay_signature
                tx.status = 'success'
                tx.save()
            except Transaction.DoesNotExist:
                pass
                
            return Response({'status': 'Payment verified successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            # Payment failed or signature verification failed
            try:
                tx = Transaction.objects.get(razorpay_order_id=razorpay_order_id)
                tx.status = 'failed'
                tx.save()
            except:
                pass
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
