import pytest
from datetime import datetime
from src.core.models.user import (
    User, UserAddress, UserPayment, UserSession, UserNotification,
    UserPreference, UserActivity, UserVerification
)

def test_user_creation():
    user = User(
        id=1,
        telegram_id=123456789,
        username="testuser",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        role="customer",
        is_active=True,
        is_verified=True,
        language="en",
        timezone="UTC"
    )
    
    assert user.id == 1
    assert user.telegram_id == 123456789
    assert user.username == "testuser"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.phone == "+1234567890"
    assert user.role == "customer"
    assert user.is_active is True
    assert user.is_verified is True
    assert user.language == "en"
    assert user.timezone == "UTC"

def test_user_address_creation():
    address = UserAddress(
        id=1,
        user_id=1,
        type="shipping",
        full_name="John Doe",
        address_line1="123 Main St",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        phone="+1234567890",
        is_default=True
    )
    
    assert address.id == 1
    assert address.user_id == 1
    assert address.type == "shipping"
    assert address.full_name == "John Doe"
    assert address.address_line1 == "123 Main St"
    assert address.city == "New York"
    assert address.state == "NY"
    assert address.postal_code == "10001"
    assert address.country == "USA"
    assert address.phone == "+1234567890"
    assert address.is_default is True

def test_user_payment_creation():
    payment = UserPayment(
        id=1,
        user_id=1,
        method="credit_card",
        details={"last4": "4242", "brand": "visa"},
        is_default=True,
        is_active=True
    )
    
    assert payment.id == 1
    assert payment.user_id == 1
    assert payment.method == "credit_card"
    assert isinstance(payment.details, dict)
    assert payment.is_default is True
    assert payment.is_active is True

def test_user_session_creation():
    session = UserSession(
        id=1,
        user_id=1,
        token="session_token_123",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        expires_at=datetime.now()
    )
    
    assert session.id == 1
    assert session.user_id == 1
    assert session.token == "session_token_123"
    assert session.ip_address == "192.168.1.1"
    assert session.user_agent == "Mozilla/5.0"
    assert isinstance(session.expires_at, datetime)

def test_user_notification_creation():
    notification = UserNotification(
        id=1,
        user_id=1,
        type="order_status",
        title="Order Confirmed",
        message="Your order #123 has been confirmed",
        is_read=False,
        data={"order_id": 123, "status": "confirmed"}
    )
    
    assert notification.id == 1
    assert notification.user_id == 1
    assert notification.type == "order_status"
    assert notification.title == "Order Confirmed"
    assert notification.message == "Your order #123 has been confirmed"
    assert notification.is_read is False
    assert isinstance(notification.data, dict)

def test_user_preference_creation():
    preference = UserPreference(
        id=1,
        user_id=1,
        key="email_notifications",
        value=True,
        category="notifications"
    )
    
    assert preference.id == 1
    assert preference.user_id == 1
    assert preference.key == "email_notifications"
    assert preference.value is True
    assert preference.category == "notifications"

def test_user_activity_creation():
    activity = UserActivity(
        id=1,
        user_id=1,
        type="login",
        details="User logged in from new device",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )
    
    assert activity.id == 1
    assert activity.user_id == 1
    assert activity.type == "login"
    assert activity.details == "User logged in from new device"
    assert activity.ip_address == "192.168.1.1"
    assert activity.user_agent == "Mozilla/5.0"

def test_user_verification_creation():
    verification = UserVerification(
        id=1,
        user_id=1,
        type="email",
        token="verification_token_123",
        expires_at=datetime.now(),
        is_verified=False
    )
    
    assert verification.id == 1
    assert verification.user_id == 1
    assert verification.type == "email"
    assert verification.token == "verification_token_123"
    assert isinstance(verification.expires_at, datetime)
    assert verification.is_verified is False 