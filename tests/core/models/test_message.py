import pytest
from datetime import datetime
from src.core.models.message import (
    Message, MessageType, MessageTemplate,
    MessageChannel, MessageRecipient, MessageSchedule,
    MessagePreference, MessageHistory, MessageGroup,
    MessageRule
)

def test_message_creation():
    message = Message(
        id=1,
        type="welcome",
        title="Welcome to Our Store",
        content="Thank you for joining our store!",
        data={
            "store_name": "My Store",
            "discount_code": "WELCOME10"
        },
        priority="normal",
        is_read=False,
        created_at=datetime.now()
    )
    
    assert message.id == 1
    assert message.type == "welcome"
    assert message.title == "Welcome to Our Store"
    assert message.content == "Thank you for joining our store!"
    assert isinstance(message.data, dict)
    assert message.priority == "normal"
    assert message.is_read is False
    assert isinstance(message.created_at, datetime)

def test_message_type_creation():
    type = MessageType(
        id=1,
        name="welcome",
        description="Welcome messages",
        category="system",
        is_active=True
    )
    
    assert type.id == 1
    assert type.name == "welcome"
    assert type.description == "Welcome messages"
    assert type.category == "system"
    assert type.is_active is True

def test_message_template_creation():
    template = MessageTemplate(
        id=1,
        type_id=1,
        name="Welcome Message",
        subject="Welcome to {store_name}",
        body="Dear {customer_name},\n\nWelcome to {store_name}!",
        variables=["store_name", "customer_name"],
        is_active=True
    )
    
    assert template.id == 1
    assert template.type_id == 1
    assert template.name == "Welcome Message"
    assert template.subject == "Welcome to {store_name}"
    assert template.body == "Dear {customer_name},\n\nWelcome to {store_name}!"
    assert isinstance(template.variables, list)
    assert template.is_active is True

def test_message_channel_creation():
    channel = MessageChannel(
        id=1,
        name="telegram",
        description="Telegram messages",
        provider="telegram_bot",
        settings={
            "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "chat_id": "-100123456789"
        },
        is_active=True
    )
    
    assert channel.id == 1
    assert channel.name == "telegram"
    assert channel.description == "Telegram messages"
    assert channel.provider == "telegram_bot"
    assert isinstance(channel.settings, dict)
    assert channel.is_active is True

def test_message_recipient_creation():
    recipient = MessageRecipient(
        id=1,
        message_id=1,
        user_id=100,
        channel_id=1,
        status="pending",
        sent_at=None
    )
    
    assert recipient.id == 1
    assert recipient.message_id == 1
    assert recipient.user_id == 100
    assert recipient.channel_id == 1
    assert recipient.status == "pending"
    assert recipient.sent_at is None

def test_message_schedule_creation():
    schedule = MessageSchedule(
        id=1,
        name="Daily Newsletter",
        description="Send daily newsletter",
        frequency="daily",
        time="10:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.name == "Daily Newsletter"
    assert schedule.description == "Send daily newsletter"
    assert schedule.frequency == "daily"
    assert schedule.time == "10:00"
    assert schedule.is_active is True

def test_message_preference_creation():
    preference = MessagePreference(
        id=1,
        user_id=100,
        type_id=1,
        channel_id=1,
        is_enabled=True,
        quiet_hours_start="23:00",
        quiet_hours_end="09:00"
    )
    
    assert preference.id == 1
    assert preference.user_id == 100
    assert preference.type_id == 1
    assert preference.channel_id == 1
    assert preference.is_enabled is True
    assert preference.quiet_hours_start == "23:00"
    assert preference.quiet_hours_end == "09:00"

def test_message_history_creation():
    history = MessageHistory(
        id=1,
        message_id=1,
        recipient_id=1,
        channel_id=1,
        status="sent",
        error_message=None,
        sent_at=datetime.now()
    )
    
    assert history.id == 1
    assert history.message_id == 1
    assert history.recipient_id == 1
    assert history.channel_id == 1
    assert history.status == "sent"
    assert history.error_message is None
    assert isinstance(history.sent_at, datetime)

def test_message_group_creation():
    group = MessageGroup(
        id=1,
        name="Newsletter Subscribers",
        description="Newsletter subscriber group",
        criteria={
            "subscribed": True,
            "last_activity": "30d"
        },
        is_active=True
    )
    
    assert group.id == 1
    assert group.name == "Newsletter Subscribers"
    assert group.description == "Newsletter subscriber group"
    assert isinstance(group.criteria, dict)
    assert group.is_active is True

def test_message_rule_creation():
    rule = MessageRule(
        id=1,
        name="New User Welcome",
        description="Send welcome message to new users",
        condition={
            "event": "user_registration",
            "days_since_registration": 0
        },
        action={
            "type": "send_message",
            "template_id": 1,
            "channel_id": 1
        },
        is_active=True
    )
    
    assert rule.id == 1
    assert rule.name == "New User Welcome"
    assert rule.description == "Send welcome message to new users"
    assert isinstance(rule.condition, dict)
    assert isinstance(rule.action, dict)
    assert rule.is_active is True 