from datetime import datetime
from typing import Dict, Any, Optional
from src.core.models import Payment, Order
from src.core.exceptions import PaymentError, ValidationError
from src.core.validators import Validators

class PaymentManager:
    def initiate_payment(self, payment_data: Dict[str, Any]) -> Payment:
        """Initiate a new payment"""
        try:
            # Validate payment data
            if 'amount' not in payment_data or payment_data['amount'] <= 0:
                raise ValidationError("Invalid payment amount")
            
            # Get order
            order = Order.get_by_id(payment_data['order_id'])
            if not order:
                raise PaymentError("Order not found")
            
            # Create payment
            payment = Payment(
                order_id=order.id,
                amount=payment_data['amount'],
                currency=payment_data.get('currency', 'USDT'),
                payment_method=payment_data.get('payment_method', 'crypto'),
                status='pending',
                created_at=datetime.utcnow()
            )
            payment.save()
            
            return payment
        except Exception as e:
            raise PaymentError(f"Failed to initiate payment: {str(e)}")

    def process_payment(self, payment_id: int, transaction_hash: str) -> Dict[str, Any]:
        """Process a payment with transaction hash"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                raise PaymentError("Payment not found")
            
            # Validate transaction hash
            Validators.validate_transaction_hash(transaction_hash)
            
            # Update payment status
            payment.status = 'completed'
            payment.transaction_hash = transaction_hash
            payment.completed_at = datetime.utcnow()
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'paid'
            order.updated_at = datetime.utcnow()
            order.save()
            
            return {
                "success": True,
                "payment": payment,
                "order": order
            }
        except Exception as e:
            raise PaymentError(f"Failed to process payment: {str(e)}")

    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        try:
            return Payment.get_by_id(payment_id)
        except Exception as e:
            raise PaymentError(f"Failed to get payment: {str(e)}")

    def get_payment_status(self, payment_id: int) -> str:
        """Get payment status"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                raise PaymentError("Payment not found")
            return payment.status
        except Exception as e:
            raise PaymentError(f"Failed to get payment status: {str(e)}")

    def refund_payment(self, payment_id: int) -> Dict[str, Any]:
        """Refund a payment"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                raise PaymentError("Payment not found")
            
            if payment.status != 'completed':
                raise PaymentError("Only completed payments can be refunded")
            
            # Update payment status
            payment.status = 'refunded'
            payment.refunded_at = datetime.utcnow()
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'refunded'
            order.updated_at = datetime.utcnow()
            order.save()
            
            return {
                "success": True,
                "payment": payment,
                "order": order
            }
        except Exception as e:
            raise PaymentError(f"Failed to refund payment: {str(e)}")

    def get_order_payments(self, order_id: int) -> list[Payment]:
        """Get all payments for an order"""
        try:
            return Payment.get_by_order_id(order_id)
        except Exception as e:
            raise PaymentError(f"Failed to get order payments: {str(e)}")

    def validate_payment(self, payment_id: int) -> bool:
        """Validate payment data and status"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                return False
            
            order = payment.order
            if not order:
                return False
            
            if payment.amount != order.total_amount:
                return False
            
            return True
        except Exception:
            return False
