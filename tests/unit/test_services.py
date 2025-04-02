import pytest
from datetime import datetime
from src.core.services.order_manager import OrderManager
from src.core.services.crypto_manager import CryptoManager

@pytest.fixture
def order_manager():
    return OrderManager()

@pytest.fixture
def crypto_manager():
    return CryptoManager()

class TestOrderManager:
    def test_create_order(self, order_manager):
        order_data = {
            "user_id": 123456789,
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ],
            "total_amount": 150.0,
            "payment_method": "crypto"
        }
        order = order_manager.create_order(order_data)
        assert order.user_id == order_data["user_id"]
        assert order.total_amount == order_data["total_amount"]
        assert order.payment_method == order_data["payment_method"]
        assert order.status == "pending"
        assert isinstance(order.created_at, datetime)

    def test_update_order_status(self, order_manager):
        order_data = {
            "user_id": 123456789,
            "items": [{"product_id": 1, "quantity": 1}],
            "total_amount": 50.0,
            "payment_method": "crypto"
        }
        order = order_manager.create_order(order_data)
        updated_order = order_manager.update_order_status(order.id, "paid")
        assert updated_order.status == "paid"
        assert isinstance(updated_order.updated_at, datetime)

    def test_get_user_orders(self, order_manager):
        user_id = 123456789
        order_data = {
            "user_id": user_id,
            "items": [{"product_id": 1, "quantity": 1}],
            "total_amount": 50.0,
            "payment_method": "crypto"
        }
        order_manager.create_order(order_data)
        orders = order_manager.get_user_orders(user_id)
        assert len(orders) > 0
        assert all(order.user_id == user_id for order in orders)

class TestCryptoManager:
    def test_generate_wallet_address(self, crypto_manager):
        address = crypto_manager.generate_wallet_address()
        assert isinstance(address, str)
        assert len(address) > 0
        assert address.startswith("TR")  # Assuming TRC20 network

    def test_verify_transaction(self, crypto_manager):
        tx_hash = "test_transaction_hash"
        amount = 100.0
        result = crypto_manager.verify_transaction(tx_hash, amount)
        assert isinstance(result, bool)

    def test_get_balance(self, crypto_manager):
        address = crypto_manager.generate_wallet_address()
        balance = crypto_manager.get_balance(address)
        assert isinstance(balance, float)
        assert balance >= 0

    def test_send_transaction(self, crypto_manager):
        from_address = crypto_manager.generate_wallet_address()
        to_address = crypto_manager.generate_wallet_address()
        amount = 50.0
        result = crypto_manager.send_transaction(from_address, to_address, amount)
        assert isinstance(result, dict)
        assert "success" in result
        assert "tx_hash" in result
