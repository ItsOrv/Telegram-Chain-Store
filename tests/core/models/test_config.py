import pytest
from datetime import datetime
from src.core.models.config import (
    Config, Permission, AuthConfig, DatabaseConfig, AnalyticsConfig,
    SystemConfig, UserConfig, StoreConfig
)

def test_config_creation():
    config = Config(
        id=1,
        key="site_name",
        value="My Store",
        description="Store name",
        category="general",
        is_system=False
    )
    
    assert config.id == 1
    assert config.key == "site_name"
    assert config.value == "My Store"
    assert config.description == "Store name"
    assert config.category == "general"
    assert config.is_system is False

def test_permission_creation():
    permission = Permission(
        id=1,
        name="manage_products",
        description="Can manage products",
        category="products",
        is_active=True
    )
    
    assert permission.id == 1
    assert permission.name == "manage_products"
    assert permission.description == "Can manage products"
    assert permission.category == "products"
    assert permission.is_active is True

def test_auth_config_creation():
    auth = AuthConfig(
        id=1,
        store_id=1,
        login_method="telegram",
        require_verification=True,
        session_timeout=3600,
        max_login_attempts=5,
        lockout_duration=1800
    )
    
    assert auth.id == 1
    assert auth.store_id == 1
    assert auth.login_method == "telegram"
    assert auth.require_verification is True
    assert auth.session_timeout == 3600
    assert auth.max_login_attempts == 5
    assert auth.lockout_duration == 1800

def test_database_config_creation():
    db = DatabaseConfig(
        id=1,
        store_id=1,
        type="postgresql",
        host="localhost",
        port=5432,
        database="mystore",
        username="admin",
        password="secret",
        is_active=True
    )
    
    assert db.id == 1
    assert db.store_id == 1
    assert db.type == "postgresql"
    assert db.host == "localhost"
    assert db.port == 5432
    assert db.database == "mystore"
    assert db.username == "admin"
    assert db.password == "secret"
    assert db.is_active is True

def test_analytics_config_creation():
    analytics = AnalyticsConfig(
        id=1,
        store_id=1,
        provider="google_analytics",
        tracking_id="UA-123456789",
        is_active=True,
        settings={
            "track_pageviews": True,
            "track_events": True,
            "track_ecommerce": True
        }
    )
    
    assert analytics.id == 1
    assert analytics.store_id == 1
    assert analytics.provider == "google_analytics"
    assert analytics.tracking_id == "UA-123456789"
    assert analytics.is_active is True
    assert isinstance(analytics.settings, dict)

def test_system_config_creation():
    system = SystemConfig(
        id=1,
        store_id=1,
        maintenance_mode=False,
        debug_mode=False,
        timezone="UTC",
        language="en",
        currency="USD",
        date_format="YYYY-MM-DD"
    )
    
    assert system.id == 1
    assert system.store_id == 1
    assert system.maintenance_mode is False
    assert system.debug_mode is False
    assert system.timezone == "UTC"
    assert system.language == "en"
    assert system.currency == "USD"
    assert system.date_format == "YYYY-MM-DD"

def test_user_config_creation():
    user = UserConfig(
        id=1,
        store_id=1,
        allow_registration=True,
        require_email=True,
        require_phone=True,
        min_password_length=8,
        password_expiry_days=90
    )
    
    assert user.id == 1
    assert user.store_id == 1
    assert user.allow_registration is True
    assert user.require_email is True
    assert user.require_phone is True
    assert user.min_password_length == 8
    assert user.password_expiry_days == 90

def test_store_config_creation():
    store = StoreConfig(
        id=1,
        store_id=1,
        name="My Store",
        description="My online store",
        logo_url="https://example.com/logo.png",
        favicon_url="https://example.com/favicon.ico",
        contact_email="support@example.com",
        contact_phone="+1234567890",
        address={
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA"
        }
    )
    
    assert store.id == 1
    assert store.store_id == 1
    assert store.name == "My Store"
    assert store.description == "My online store"
    assert store.logo_url == "https://example.com/logo.png"
    assert store.favicon_url == "https://example.com/favicon.ico"
    assert store.contact_email == "support@example.com"
    assert store.contact_phone == "+1234567890"
    assert isinstance(store.address, dict) 