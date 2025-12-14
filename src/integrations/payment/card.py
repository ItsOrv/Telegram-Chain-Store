from decimal import Decimal
from datetime import datetime
from typing import Optional
from core.models import Payment, Order
from core.database import SessionLocal
from core.crypto_manager import crypto_manager
from core.exceptions import PaymentError
import logging

logger = logging.getLogger(__name__)

class PaymentManager:
    @staticmethod
    async def create_payment(order_id: str, payment_method: str) -> dict:
        """Create new payment for order"""
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if not order:
                raise PaymentError("Order not found")

            if payment_method == "crypto":
                payment_data = await crypto_manager.create_payment(
                    amount=order.total_price,
                    order_id=order_id
                )
            elif payment_method == "card":
                # Handle card payment
                payment_data = {
                    "card_number": "xxxx-xxxx-xxxx-xxxx",
                    "amount": order.total_price
                }
            else:
                raise PaymentError("Invalid payment method")

            # Create payment record
            payment = Payment(
                order_id=order_id,
                amount=order.total_price,
                payment_method=payment_method,
                status="pending"
            )
            db.add(payment)
            db.commit()

            return payment_data

    @staticmethod
    async def verify_payment(payment_id: str) -> bool:
        """Verify payment status"""
        with SessionLocal() as db:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                return False

            if payment.payment_method == "crypto":
                verified = await crypto_manager.verify_transaction(
                    payment.transaction_id
                )
            else:
                # Verify card payment
                verified = True  # Implement actual verification

            if verified:
                payment.status = "completed"
                payment.completed_at = datetime.now()
                db.commit()

            return verified

from typing import Optional
from datetime import datetime
from core.models import Payment, PaymentMethod
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class PaymentManager:
    @staticmethod
    async def create_crypto_payment(order_id: str, amount: float) -> Optional[dict]:
        """Create a new crypto payment request"""
        try:
            # اینجا باید به API صرافی یا درگاه کریپتو متصل شوید
            # و درخواست پرداخت ایجاد کنید
            payment_data = {
                'address': settings.CRYPTO_WALLET_ADDRESS,
                'amount': amount,
                'currency': 'USDT',
                'order_id': order_id
            }
            return payment_data
        except Exception as e:
            logger.error(f"Error creating crypto payment: {e}")
            return None

    @staticmethod
    async def create_card_payment(order_id: str, amount: float) -> Optional[dict]:
        """Create a new card-to-card payment request"""
        try:
            # اطلاعات کارت فروشنده را برگردانید
            payment_data = {
                'card_number': settings.MERCHANT_CARD_NUMBER,
                'amount': amount,
                'order_id': order_id
            }
            return payment_data
        except Exception as e:
            logger.error(f"Error creating card payment: {e}")
            return None

    @staticmethod
    async def verify_payment(payment_id: str, payment_method: PaymentMethod) -> bool:
        """Verify payment status"""
        try:
            if payment_method == PaymentMethod.CRYPTO:
                # بررسی تراکنش در شبکه بلاکچین
                pass
            elif payment_method == PaymentMethod.CARD:
                # بررسی رسید پرداخت کارت به کارت
                pass
            return True
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return False


