import pytest
from datetime import datetime
from src.core.models.discount import (
    Discount, DiscountRule, DiscountUsage, DiscountProduct,
    DiscountCategory, DiscountCustomer, DiscountHistory, DiscountReport
)

def test_discount_creation():
    discount = Discount(
        id=1,
        name="Summer Sale",
        type="percentage",
        value=20.0,
        store_id=1,
        description="Summer sale discount",
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_active=True,
        minimum_spend=100.0,
        maximum_spend=1000.0,
        usage_limit=1000
    )
    
    assert discount.id == 1
    assert discount.name == "Summer Sale"
    assert discount.type == "percentage"
    assert discount.value == 20.0
    assert discount.store_id == 1
    assert discount.description == "Summer sale discount"
    assert isinstance(discount.start_date, datetime)
    assert isinstance(discount.end_date, datetime)
    assert discount.is_active is True
    assert discount.minimum_spend == 100.0
    assert discount.maximum_spend == 1000.0
    assert discount.usage_limit == 1000

def test_discount_rule_creation():
    rule = DiscountRule(
        id=1,
        discount_id=1,
        rule_type="minimum_quantity",
        conditions={"min_quantity": 2, "product_ids": [1, 2, 3]}
    )
    
    assert rule.id == 1
    assert rule.discount_id == 1
    assert rule.rule_type == "minimum_quantity"
    assert isinstance(rule.conditions, dict)
    assert "min_quantity" in rule.conditions
    assert "product_ids" in rule.conditions

def test_discount_usage_creation():
    usage = DiscountUsage(
        id=1,
        discount_id=1,
        user_id=100,
        order_id=1,
        amount=20.0
    )
    
    assert usage.id == 1
    assert usage.discount_id == 1
    assert usage.user_id == 100
    assert usage.order_id == 1
    assert usage.amount == 20.0

def test_discount_product_creation():
    product = DiscountProduct(
        id=1,
        discount_id=1,
        product_id=1
    )
    
    assert product.id == 1
    assert product.discount_id == 1
    assert product.product_id == 1

def test_discount_category_creation():
    category = DiscountCategory(
        id=1,
        discount_id=1,
        category_id=1
    )
    
    assert category.id == 1
    assert category.discount_id == 1
    assert category.category_id == 1

def test_discount_customer_creation():
    customer = DiscountCustomer(
        id=1,
        discount_id=1,
        customer_id=100
    )
    
    assert customer.id == 1
    assert customer.discount_id == 1
    assert customer.customer_id == 100

def test_discount_history_creation():
    history = DiscountHistory(
        id=1,
        discount_id=1,
        action="created",
        user_id=100
    )
    
    assert history.id == 1
    assert history.discount_id == 1
    assert history.action == "created"
    assert history.user_id == 100

def test_discount_report_creation():
    report = DiscountReport(
        id=1,
        discount_id=1,
        total_usage=500,
        total_amount=10000.0,
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    
    assert report.id == 1
    assert report.discount_id == 1
    assert report.total_usage == 500
    assert report.total_amount == 10000.0
    assert isinstance(report.start_date, datetime)
    assert isinstance(report.end_date, datetime) 