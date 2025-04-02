import pytest
from datetime import datetime
from src.core.models.notification import (
    Notification, NotificationType, NotificationTemplate,
    NotificationChannel, NotificationRecipient, NotificationSchedule,
    NotificationPreference, NotificationHistory, NotificationGroup,
    NotificationRule
)

def test_notification_creation():
    notification = Notification(
        id=1,
        type="order_status",
        title="Order Confirmed",
        message="Your order #123 has been confirmed",
        data={
            "order_id": 123,
            "status": "confirmed",
            "amount": 100.0
        },
        priority="high",
        is_read=False,
        created_at=datetime.now()
    )
    
    assert notification.id == 1
    assert notification.type == "order_status"
    assert notification.title == "Order Confirmed"
    assert notification.message == "Your order #123 has been confirmed"
    assert isinstance(notification.data, dict)
    assert notification.priority == "high"
    assert notification.is_read is False
    assert isinstance(notification.created_at, datetime)

def test_notification_type_creation():
    type = NotificationType(
        id=1,
        name="order_status",
        description="Order status updates",
        category="orders",
        is_active=True
    )
    
    assert type.id == 1
    assert type.name == "order_status"
    assert type.description == "Order status updates"
    assert type.category == "orders"
    assert type.is_active is True

def test_notification_template_creation():
    template = NotificationTemplate(
        id=1,
        type_id=1,
        name="Order Confirmation",
        subject="Order Confirmed - #{order_id}",
        body="Dear {customer_name},\n\nYour order #{order_id} has been confirmed.",
        variables=["order_id", "customer_name"],
        is_active=True
    )
    
    assert template.id == 1
    assert template.type_id == 1
    assert template.name == "Order Confirmation"
    assert template.subject == "Order Confirmed - #{order_id}"
    assert template.body == "Dear {customer_name},\n\nYour order #{order_id} has been confirmed."
    assert isinstance(template.variables, list)
    assert template.is_active is True

def test_notification_channel_creation():
    channel = NotificationChannel(
        id=1,
        name="email",
        description="Email notifications",
        provider="smtp",
        settings={
            "host": "smtp.example.com",
            "port": 587,
            "username": "noreply@example.com"
        },
        is_active=True
    )
    
    assert channel.id == 1
    assert channel.name == "email"
    assert channel.description == "Email notifications"
    assert channel.provider == "smtp"
    assert isinstance(channel.settings, dict)
    assert channel.is_active is True

def test_notification_recipient_creation():
    recipient = NotificationRecipient(
        id=1,
        notification_id=1,
        user_id=100,
        channel_id=1,
        status="pending",
        sent_at=None
    )
    
    assert recipient.id == 1
    assert recipient.notification_id == 1
    assert recipient.user_id == 100
    assert recipient.channel_id == 1
    assert recipient.status == "pending"
    assert recipient.sent_at is None

def test_notification_schedule_creation():
    schedule = NotificationSchedule(
        id=1,
        name="Order Reminder",
        description="Send order reminder notifications",
        frequency="daily",
        time="09:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.name == "Order Reminder"
    assert schedule.description == "Send order reminder notifications"
    assert schedule.frequency == "daily"
    assert schedule.time == "09:00"
    assert schedule.is_active is True

def test_notification_preference_creation():
    preference = NotificationPreference(
        id=1,
        user_id=100,
        type_id=1,
        channel_id=1,
        is_enabled=True,
        quiet_hours_start="22:00",
        quiet_hours_end="08:00"
    )
    
    assert preference.id == 1
    assert preference.user_id == 100
    assert preference.type_id == 1
    assert preference.channel_id == 1
    assert preference.is_enabled is True
    assert preference.quiet_hours_start == "22:00"
    assert preference.quiet_hours_end == "08:00"

def test_notification_history_creation():
    history = NotificationHistory(
        id=1,
        notification_id=1,
        recipient_id=1,
        channel_id=1,
        status="sent",
        error_message=None,
        sent_at=datetime.now()
    )
    
    assert history.id == 1
    assert history.notification_id == 1
    assert history.recipient_id == 1
    assert history.channel_id == 1
    assert history.status == "sent"
    assert history.error_message is None
    assert isinstance(history.sent_at, datetime)

def test_notification_group_creation():
    group = NotificationGroup(
        id=1,
        name="VIP Customers",
        description="VIP customer notifications",
        criteria={
            "min_orders": 10,
            "min_spent": 1000.0
        },
        is_active=True
    )
    
    assert group.id == 1
    assert group.name == "VIP Customers"
    assert group.description == "VIP customer notifications"
    assert isinstance(group.criteria, dict)
    assert group.is_active is True

def test_notification_rule_creation():
    rule = NotificationRule(
        id=1,
        name="Order Status Change",
        description="Send notification on order status change",
        condition={
            "event": "order_status_change",
            "old_status": "pending",
            "new_status": "confirmed"
        },
        action={
            "type": "send_notification",
            "template_id": 1,
            "channel_id": 1
        },
        is_active=True
    )
    
    assert rule.id == 1
    assert rule.name == "Order Status Change"
    assert rule.description == "Send notification on order status change"
    assert isinstance(rule.condition, dict)
    assert isinstance(rule.action, dict)
    assert rule.is_active is True 