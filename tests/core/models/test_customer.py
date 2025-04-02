import pytest
from datetime import datetime
from src.core.models.customer import (
    Customer, CustomerAddress, CustomerGroup, CustomerGroupMembership,
    CustomerNote, CustomerPreference, CustomerActivity, CustomerSegment,
    CustomerTag
)

def test_customer_creation():
    customer = Customer(
        id=1,
        user_id=100,
        store_id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        total_orders=10,
        total_spent=1000.0,
        last_order_date=datetime.now(),
        is_active=True,
        is_verified=True
    )
    
    assert customer.id == 1
    assert customer.user_id == 100
    assert customer.store_id == 1
    assert customer.first_name == "John"
    assert customer.last_name == "Doe"
    assert customer.email == "john@example.com"
    assert customer.phone == "+1234567890"
    assert customer.total_orders == 10
    assert customer.total_spent == 1000.0
    assert isinstance(customer.last_order_date, datetime)
    assert customer.is_active is True
    assert customer.is_verified is True

def test_customer_address_creation():
    address = CustomerAddress(
        id=1,
        customer_id=1,
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
    assert address.customer_id == 1
    assert address.type == "shipping"
    assert address.full_name == "John Doe"
    assert address.address_line1 == "123 Main St"
    assert address.city == "New York"
    assert address.state == "NY"
    assert address.postal_code == "10001"
    assert address.country == "USA"
    assert address.phone == "+1234567890"
    assert address.is_default is True

def test_customer_group_creation():
    group = CustomerGroup(
        id=1,
        name="VIP Customers",
        description="High-value customers",
        store_id=1,
        is_active=True
    )
    
    assert group.id == 1
    assert group.name == "VIP Customers"
    assert group.description == "High-value customers"
    assert group.store_id == 1
    assert group.is_active is True

def test_customer_group_membership_creation():
    membership = CustomerGroupMembership(
        id=1,
        customer_id=1,
        group_id=1,
        joined_at=datetime.now()
    )
    
    assert membership.id == 1
    assert membership.customer_id == 1
    assert membership.group_id == 1
    assert isinstance(membership.joined_at, datetime)

def test_customer_note_creation():
    note = CustomerNote(
        id=1,
        customer_id=1,
        user_id=100,
        note="Customer prefers email communication",
        is_internal=True
    )
    
    assert note.id == 1
    assert note.customer_id == 1
    assert note.user_id == 100
    assert note.note == "Customer prefers email communication"
    assert note.is_internal is True

def test_customer_preference_creation():
    preference = CustomerPreference(
        id=1,
        customer_id=1,
        key="marketing_emails",
        value=True,
        category="communications"
    )
    
    assert preference.id == 1
    assert preference.customer_id == 1
    assert preference.key == "marketing_emails"
    assert preference.value is True
    assert preference.category == "communications"

def test_customer_activity_creation():
    activity = CustomerActivity(
        id=1,
        customer_id=1,
        type="purchase",
        details="Purchased product X",
        amount=100.0,
        metadata={"product_id": 1, "order_id": 123}
    )
    
    assert activity.id == 1
    assert activity.customer_id == 1
    assert activity.type == "purchase"
    assert activity.details == "Purchased product X"
    assert activity.amount == 100.0
    assert isinstance(activity.metadata, dict)

def test_customer_segment_creation():
    segment = CustomerSegment(
        id=1,
        name="High Value",
        description="Customers who spent over $1000",
        store_id=1,
        criteria={"min_spent": 1000.0},
        is_active=True
    )
    
    assert segment.id == 1
    assert segment.name == "High Value"
    assert segment.description == "Customers who spent over $1000"
    assert segment.store_id == 1
    assert isinstance(segment.criteria, dict)
    assert segment.is_active is True

def test_customer_tag_creation():
    tag = CustomerTag(
        id=1,
        name="Early Adopter",
        store_id=1,
        is_active=True
    )
    
    assert tag.id == 1
    assert tag.name == "Early Adopter"
    assert tag.store_id == 1
    assert tag.is_active is True 