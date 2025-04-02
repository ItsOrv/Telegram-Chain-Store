import pytest
from datetime import datetime
from src.core.models.order import (
    Order, OrderItem, OrderPayment, OrderShipment, OrderRefund,
    OrderNote, OrderDiscount, OrderTax, OrderHistory
)

def test_order_creation():
    order = Order(
        id=1,
        user_id=100,
        store_id=1,
        status="pending",
        total_amount=100.0,
        shipping_address={
            "full_name": "John Doe",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA"
        },
        payment_method="credit_card",
        shipping_method="standard"
    )
    
    assert order.id == 1
    assert order.user_id == 100
    assert order.store_id == 1
    assert order.status == "pending"
    assert order.total_amount == 100.0
    assert isinstance(order.shipping_address, dict)
    assert order.payment_method == "credit_card"
    assert order.shipping_method == "standard"

def test_order_item_creation():
    item = OrderItem(
        id=1,
        order_id=1,
        product_id=1,
        variant_id=1,
        quantity=2,
        unit_price=50.0,
        total_price=100.0,
        discount_amount=10.0,
        tax_amount=5.0
    )
    
    assert item.id == 1
    assert item.order_id == 1
    assert item.product_id == 1
    assert item.variant_id == 1
    assert item.quantity == 2
    assert item.unit_price == 50.0
    assert item.total_price == 100.0
    assert item.discount_amount == 10.0
    assert item.tax_amount == 5.0

def test_order_payment_creation():
    payment = OrderPayment(
        id=1,
        order_id=1,
        amount=100.0,
        payment_method="credit_card",
        status="completed",
        transaction_id="tx_123456"
    )
    
    assert payment.id == 1
    assert payment.order_id == 1
    assert payment.amount == 100.0
    assert payment.payment_method == "credit_card"
    assert payment.status == "completed"
    assert payment.transaction_id == "tx_123456"

def test_order_shipment_creation():
    shipment = OrderShipment(
        id=1,
        order_id=1,
        carrier="FedEx",
        tracking_number="FDX123456",
        status="in_transit",
        shipping_address={
            "full_name": "John Doe",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA"
        }
    )
    
    assert shipment.id == 1
    assert shipment.order_id == 1
    assert shipment.carrier == "FedEx"
    assert shipment.tracking_number == "FDX123456"
    assert shipment.status == "in_transit"
    assert isinstance(shipment.shipping_address, dict)

def test_order_refund_creation():
    refund = OrderRefund(
        id=1,
        order_id=1,
        amount=50.0,
        reason="Customer request",
        status="completed",
        refund_method="credit_card"
    )
    
    assert refund.id == 1
    assert refund.order_id == 1
    assert refund.amount == 50.0
    assert refund.reason == "Customer request"
    assert refund.status == "completed"
    assert refund.refund_method == "credit_card"

def test_order_note_creation():
    note = OrderNote(
        id=1,
        order_id=1,
        user_id=100,
        note="Customer requested gift wrapping",
        is_internal=True
    )
    
    assert note.id == 1
    assert note.order_id == 1
    assert note.user_id == 100
    assert note.note == "Customer requested gift wrapping"
    assert note.is_internal is True

def test_order_discount_creation():
    discount = OrderDiscount(
        id=1,
        order_id=1,
        code="SUMMER2024",
        type="percentage",
        value=10.0
    )
    
    assert discount.id == 1
    assert discount.order_id == 1
    assert discount.code == "SUMMER2024"
    assert discount.type == "percentage"
    assert discount.value == 10.0

def test_order_tax_creation():
    tax = OrderTax(
        id=1,
        order_id=1,
        name="VAT",
        rate=0.1,
        amount=10.0
    )
    
    assert tax.id == 1
    assert tax.order_id == 1
    assert tax.name == "VAT"
    assert tax.rate == 0.1
    assert tax.amount == 10.0

def test_order_history_creation():
    history = OrderHistory(
        id=1,
        order_id=1,
        status="processing",
        user_id=100,
        comment="Order moved to processing"
    )
    
    assert history.id == 1
    assert history.order_id == 1
    assert history.status == "processing"
    assert history.user_id == 100
    assert history.comment == "Order moved to processing" 