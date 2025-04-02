import pytest
from datetime import datetime
from src.core.models.cart import (
    Cart, CartItem, CartDiscount, CartTax, CartShipping,
    CartAddress, CartPaymentMethod, CartHistory, SavedCart
)

def test_cart_creation():
    cart = Cart(
        id=1,
        user_id=100,
        session_id="session_123",
        store_id=1,
        status="active",
        currency="USD"
    )
    
    assert cart.id == 1
    assert cart.user_id == 100
    assert cart.session_id == "session_123"
    assert cart.store_id == 1
    assert cart.status == "active"
    assert cart.currency == "USD"

def test_cart_item_creation():
    item = CartItem(
        id=1,
        cart_id=1,
        product_id=1,
        variant_id=1,
        quantity=2,
        unit_price=50.0,
        total_price=100.0,
        notes="Gift wrapping requested"
    )
    
    assert item.id == 1
    assert item.cart_id == 1
    assert item.product_id == 1
    assert item.variant_id == 1
    assert item.quantity == 2
    assert item.unit_price == 50.0
    assert item.total_price == 100.0
    assert item.notes == "Gift wrapping requested"

def test_cart_discount_creation():
    discount = CartDiscount(
        id=1,
        cart_id=1,
        code="SUMMER2024",
        type="percentage",
        value=10.0
    )
    
    assert discount.id == 1
    assert discount.cart_id == 1
    assert discount.code == "SUMMER2024"
    assert discount.type == "percentage"
    assert discount.value == 10.0

def test_cart_tax_creation():
    tax = CartTax(
        id=1,
        cart_id=1,
        name="VAT",
        rate=0.1,
        amount=10.0
    )
    
    assert tax.id == 1
    assert tax.cart_id == 1
    assert tax.name == "VAT"
    assert tax.rate == 0.1
    assert tax.amount == 10.0

def test_cart_shipping_creation():
    shipping = CartShipping(
        id=1,
        cart_id=1,
        method="standard",
        cost=5.0,
        estimated_days=3
    )
    
    assert shipping.id == 1
    assert shipping.cart_id == 1
    assert shipping.method == "standard"
    assert shipping.cost == 5.0
    assert shipping.estimated_days == 3

def test_cart_address_creation():
    address = CartAddress(
        id=1,
        cart_id=1,
        type="shipping",
        full_name="John Doe",
        address_line1="123 Main St",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        phone="+1234567890"
    )
    
    assert address.id == 1
    assert address.cart_id == 1
    assert address.type == "shipping"
    assert address.full_name == "John Doe"
    assert address.address_line1 == "123 Main St"
    assert address.city == "New York"
    assert address.state == "NY"
    assert address.postal_code == "10001"
    assert address.country == "USA"
    assert address.phone == "+1234567890"

def test_cart_payment_method_creation():
    payment = CartPaymentMethod(
        id=1,
        cart_id=1,
        method="credit_card",
        details={"last4": "4242"},
        is_default=True
    )
    
    assert payment.id == 1
    assert payment.cart_id == 1
    assert payment.method == "credit_card"
    assert isinstance(payment.details, dict)
    assert payment.is_default is True

def test_cart_history_creation():
    history = CartHistory(
        id=1,
        cart_id=1,
        action="add_item",
        details="Added product to cart",
        user_id=100
    )
    
    assert history.id == 1
    assert history.cart_id == 1
    assert history.action == "add_item"
    assert history.details == "Added product to cart"
    assert history.user_id == 100

def test_saved_cart_creation():
    saved_cart = SavedCart(
        id=1,
        user_id=100,
        name="My Cart",
        cart_data={"items": [], "total": 0.0}
    )
    
    assert saved_cart.id == 1
    assert saved_cart.user_id == 100
    assert saved_cart.name == "My Cart"
    assert isinstance(saved_cart.cart_data, dict) 