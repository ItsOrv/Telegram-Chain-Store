import pytest
from datetime import datetime
from src.core.models.coupon import (
    Coupon, CouponUsage, CouponRestriction, CouponCategory,
    CouponRule, CouponBatch, CouponHistory, CouponReport
)

def test_coupon_creation():
    coupon = Coupon(
        id=1,
        code="SUMMER2024",
        type="percentage",
        value=10.0,
        store_id=1,
        description="Summer sale discount",
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_active=True,
        usage_limit=100,
        minimum_spend=50.0,
        maximum_spend=1000.0
    )
    
    assert coupon.id == 1
    assert coupon.code == "SUMMER2024"
    assert coupon.type == "percentage"
    assert coupon.value == 10.0
    assert coupon.store_id == 1
    assert coupon.description == "Summer sale discount"
    assert isinstance(coupon.start_date, datetime)
    assert isinstance(coupon.end_date, datetime)
    assert coupon.is_active is True
    assert coupon.usage_limit == 100
    assert coupon.minimum_spend == 50.0
    assert coupon.maximum_spend == 1000.0

def test_coupon_usage_creation():
    usage = CouponUsage(
        id=1,
        coupon_id=1,
        user_id=100,
        order_id=1,
        amount=10.0
    )
    
    assert usage.id == 1
    assert usage.coupon_id == 1
    assert usage.user_id == 100
    assert usage.order_id == 1
    assert usage.amount == 10.0

def test_coupon_restriction_creation():
    restriction = CouponRestriction(
        id=1,
        coupon_id=1,
        restriction_type="product",
        restriction_id=1
    )
    
    assert restriction.id == 1
    assert restriction.coupon_id == 1
    assert restriction.restriction_type == "product"
    assert restriction.restriction_id == 1

def test_coupon_category_creation():
    category = CouponCategory(
        id=1,
        name="Seasonal",
        description="Seasonal discounts",
        is_active=True
    )
    
    assert category.id == 1
    assert category.name == "Seasonal"
    assert category.description == "Seasonal discounts"
    assert category.is_active is True

def test_coupon_rule_creation():
    rule = CouponRule(
        id=1,
        coupon_id=1,
        rule_type="minimum_quantity",
        conditions={"min_quantity": 2}
    )
    
    assert rule.id == 1
    assert rule.coupon_id == 1
    assert rule.rule_type == "minimum_quantity"
    assert isinstance(rule.conditions, dict)

def test_coupon_batch_creation():
    batch = CouponBatch(
        id=1,
        name="Summer Sale 2024",
        prefix="SUMMER",
        count=100,
        length=8
    )
    
    assert batch.id == 1
    assert batch.name == "Summer Sale 2024"
    assert batch.prefix == "SUMMER"
    assert batch.count == 100
    assert batch.length == 8

def test_coupon_history_creation():
    history = CouponHistory(
        id=1,
        coupon_id=1,
        action="created",
        user_id=100
    )
    
    assert history.id == 1
    assert history.coupon_id == 1
    assert history.action == "created"
    assert history.user_id == 100

def test_coupon_report_creation():
    report = CouponReport(
        id=1,
        coupon_id=1,
        total_usage=50,
        total_amount=500.0,
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    
    assert report.id == 1
    assert report.coupon_id == 1
    assert report.total_usage == 50
    assert report.total_amount == 500.0
    assert isinstance(report.start_date, datetime)
    assert isinstance(report.end_date, datetime) 