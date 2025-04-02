import pytest
from unittest.mock import Mock, patch
from src.bot.handlers import (
    start_handler,
    help_handler,
    products_handler,
    cart_handler,
    checkout_handler,
    profile_handler
)

@pytest.fixture
def mock_message():
    message = Mock()
    message.from_user.id = 123456789
    message.from_user.username = "test_user"
    message.text = "/start"
    return message

@pytest.fixture
def mock_context():
    context = Mock()
    context.bot = Mock()
    return context

class TestHandlers:
    def test_start_handler(self, mock_message, mock_context):
        with patch('src.bot.handlers.get_user') as mock_get_user:
            mock_get_user.return_value = None
            start_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "Welcome" in mock_context.bot.send_message.call_args[0][1]

    def test_help_handler(self, mock_message, mock_context):
        help_handler(mock_message, mock_context)
        mock_context.bot.send_message.assert_called_once()
        assert "help" in mock_context.bot.send_message.call_args[0][1].lower()

    def test_products_handler(self, mock_message, mock_context):
        with patch('src.bot.handlers.get_products') as mock_get_products:
            mock_get_products.return_value = [
                {"id": 1, "name": "Test Product", "price": 100.0}
            ]
            products_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "Test Product" in mock_context.bot.send_message.call_args[0][1]

    def test_cart_handler(self, mock_message, mock_context):
        with patch('src.bot.handlers.get_cart') as mock_get_cart:
            mock_get_cart.return_value = {
                "items": [
                    {"product_id": 1, "quantity": 2, "price": 100.0}
                ],
                "total": 200.0
            }
            cart_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "200.0" in mock_context.bot.send_message.call_args[0][1]

    def test_checkout_handler(self, mock_message, mock_context):
        with patch('src.bot.handlers.process_checkout') as mock_checkout:
            mock_checkout.return_value = {
                "success": True,
                "order_id": "test_order_123"
            }
            checkout_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "success" in mock_context.bot.send_message.call_args[0][1].lower()

    def test_profile_handler(self, mock_message, mock_context):
        with patch('src.bot.handlers.get_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": 123456789,
                "username": "test_user",
                "created_at": "2024-01-01"
            }
            profile_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "test_user" in mock_context.bot.send_message.call_args[0][1]

    def test_error_handling(self, mock_message, mock_context):
        with patch('src.bot.handlers.get_products') as mock_get_products:
            mock_get_products.side_effect = Exception("Test error")
            products_handler(mock_message, mock_context)
            mock_context.bot.send_message.assert_called_once()
            assert "error" in mock_context.bot.send_message.call_args[0][1].lower()
