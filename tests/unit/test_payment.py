import pytest
from datetime import datetime
from src.core.services.payment_manager import PaymentManager

@pytest.fixture
def payment_manager():
    return PaymentManager()

class TestPaymentManager:
    def test_initiate_payment(self, payment_manager):
        payment_data = {
            "order_id": "test_order_123",
            "amount": 100.0,
            "currency": "USDT",
            "payment_method": "crypto"
        }
        payment = payment_manager.initiate_payment(payment_data)
        assert payment.order_id == payment_data["order_id"]
        assert payment.amount == payment_data["amount"]
        assert payment.currency == payment_data["currency"]
        assert payment.status == "pending"
        assert isinstance(payment.created_at, datetime)

    def test_process_payment(self, payment_manager):
        payment_data = {
            "order_id": "test_order_123",
            "amount": 100.0,
            "currency": "USDT",
            "payment_method": "crypto"
        }
        payment = payment_manager.initiate_payment(payment_data)
        result = payment_manager.process_payment(payment.id, "test_tx_hash")
        assert result["success"] is True
        assert result["payment"].status == "completed"
        assert isinstance(result["payment"].completed_at, datetime)

    def test_get_payment_status(self, payment_manager):
        payment_data = {
            "order_id": "test_order_123",
            "amount": 100.0,
            "currency": "USDT",
            "payment_method": "crypto"
        }
        payment = payment_manager.initiate_payment(payment_data)
        status = payment_manager.get_payment_status(payment.id)
        assert status == "pending"

    def test_refund_payment(self, payment_manager):
        payment_data = {
            "order_id": "test_order_123",
            "amount": 100.0,
            "currency": "USDT",
            "payment_method": "crypto"
        }
        payment = payment_manager.initiate_payment(payment_data)
        result = payment_manager.process_payment(payment.id, "test_tx_hash")
        refund = payment_manager.refund_payment(payment.id)
        assert refund["success"] is True
        assert refund["payment"].status == "refunded"
        assert isinstance(refund["payment"].refunded_at, datetime)

    def test_validate_payment_amount(self, payment_manager):
        payment_data = {
            "order_id": "test_order_123",
            "amount": -100.0,  # Invalid amount
            "currency": "USDT",
            "payment_method": "crypto"
        }
        with pytest.raises(ValueError):
            payment_manager.initiate_payment(payment_data)
