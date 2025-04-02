import pytest
from datetime import datetime
from src.core.models.store import (
    Store, StoreCategory, StoreLocation, StoreContact,
    StoreSocial, StorePayment, StoreShipping, StoreTax,
    StoreTheme, StoreDomain
)

def test_store_creation():
    store = Store(
        id=1,
        name="My Store",
        description="My online store",
        owner_id=100,
        status="active",
        type="retail",
        currency="USD",
        timezone="UTC",
        is_active=True,
        is_verified=True
    )
    
    assert store.id == 1
    assert store.name == "My Store"
    assert store.description == "My online store"
    assert store.owner_id == 100
    assert store.status == "active"
    assert store.type == "retail"
    assert store.currency == "USD"
    assert store.timezone == "UTC"
    assert store.is_active is True
    assert store.is_verified is True

def test_store_category_creation():
    category = StoreCategory(
        id=1,
        name="Electronics",
        description="Electronic products",
        parent_id=None,
        is_active=True
    )
    
    assert category.id == 1
    assert category.name == "Electronics"
    assert category.description == "Electronic products"
    assert category.parent_id is None
    assert category.is_active is True

def test_store_location_creation():
    location = StoreLocation(
        id=1,
        store_id=1,
        name="Main Store",
        address={
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA"
        },
        coordinates={"latitude": 40.7128, "longitude": -74.0060},
        is_active=True
    )
    
    assert location.id == 1
    assert location.store_id == 1
    assert location.name == "Main Store"
    assert isinstance(location.address, dict)
    assert isinstance(location.coordinates, dict)
    assert location.is_active is True

def test_store_contact_creation():
    contact = StoreContact(
        id=1,
        store_id=1,
        type="support",
        name="Support Team",
        email="support@example.com",
        phone="+1234567890",
        is_active=True
    )
    
    assert contact.id == 1
    assert contact.store_id == 1
    assert contact.type == "support"
    assert contact.name == "Support Team"
    assert contact.email == "support@example.com"
    assert contact.phone == "+1234567890"
    assert contact.is_active is True

def test_store_social_creation():
    social = StoreSocial(
        id=1,
        store_id=1,
        platform="facebook",
        url="https://facebook.com/mystore",
        is_active=True
    )
    
    assert social.id == 1
    assert social.store_id == 1
    assert social.platform == "facebook"
    assert social.url == "https://facebook.com/mystore"
    assert social.is_active is True

def test_store_payment_creation():
    payment = StorePayment(
        id=1,
        store_id=1,
        provider="stripe",
        settings={
            "publishable_key": "pk_test_123",
            "secret_key": "sk_test_123"
        },
        is_active=True
    )
    
    assert payment.id == 1
    assert payment.store_id == 1
    assert payment.provider == "stripe"
    assert isinstance(payment.settings, dict)
    assert payment.is_active is True

def test_store_shipping_creation():
    shipping = StoreShipping(
        id=1,
        store_id=1,
        provider="fedex",
        settings={
            "account_number": "123456789",
            "api_key": "api_key_123"
        },
        is_active=True
    )
    
    assert shipping.id == 1
    assert shipping.store_id == 1
    assert shipping.provider == "fedex"
    assert isinstance(shipping.settings, dict)
    assert shipping.is_active is True

def test_store_tax_creation():
    tax = StoreTax(
        id=1,
        store_id=1,
        name="VAT",
        rate=0.1,
        is_active=True
    )
    
    assert tax.id == 1
    assert tax.store_id == 1
    assert tax.name == "VAT"
    assert tax.rate == 0.1
    assert tax.is_active is True

def test_store_theme_creation():
    theme = StoreTheme(
        id=1,
        store_id=1,
        name="Modern",
        primary_color="#FF0000",
        secondary_color="#00FF00",
        font_family="Arial",
        is_active=True
    )
    
    assert theme.id == 1
    assert theme.store_id == 1
    assert theme.name == "Modern"
    assert theme.primary_color == "#FF0000"
    assert theme.secondary_color == "#00FF00"
    assert theme.font_family == "Arial"
    assert theme.is_active is True

def test_store_domain_creation():
    domain = StoreDomain(
        id=1,
        store_id=1,
        domain="mystore.com",
        is_primary=True,
        is_active=True,
        ssl_enabled=True
    )
    
    assert domain.id == 1
    assert domain.store_id == 1
    assert domain.domain == "mystore.com"
    assert domain.is_primary is True
    assert domain.is_active is True
    assert domain.ssl_enabled is True 