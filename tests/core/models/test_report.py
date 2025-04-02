import pytest
from datetime import datetime
from src.core.models.report import (
    Report, ReportType, ReportSchedule,
    ReportParameter, ReportFilter, ReportColumn,
    ReportFormat, ReportDelivery, ReportSubscription,
    ReportHistory
)

def test_report_creation():
    report = Report(
        id=1,
        name="Sales Report",
        description="Monthly sales report",
        type="sales",
        status="active",
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.name == "Sales Report"
    assert report.description == "Monthly sales report"
    assert report.type == "sales"
    assert report.status == "active"
    assert isinstance(report.created_at, datetime)

def test_report_type_creation():
    report_type = ReportType(
        id=1,
        name="Sales Analytics",
        description="Sales performance analytics",
        category="business",
        is_active=True
    )
    
    assert report_type.id == 1
    assert report_type.name == "Sales Analytics"
    assert report_type.description == "Sales performance analytics"
    assert report_type.category == "business"
    assert report_type.is_active is True

def test_report_schedule_creation():
    schedule = ReportSchedule(
        id=1,
        report_id=1,
        name="Monthly Schedule",
        description="Monthly report schedule",
        frequency="monthly",
        day_of_month=1,
        time="00:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.report_id == 1
    assert schedule.name == "Monthly Schedule"
    assert schedule.description == "Monthly report schedule"
    assert schedule.frequency == "monthly"
    assert schedule.day_of_month == 1
    assert schedule.time == "00:00"
    assert schedule.is_active is True

def test_report_parameter_creation():
    parameter = ReportParameter(
        id=1,
        report_id=1,
        name="Date Range",
        description="Report date range",
        type="date_range",
        required=True,
        default_value={
            "start": "2024-01-01",
            "end": "2024-01-31"
        }
    )
    
    assert parameter.id == 1
    assert parameter.report_id == 1
    assert parameter.name == "Date Range"
    assert parameter.description == "Report date range"
    assert parameter.type == "date_range"
    assert parameter.required is True
    assert isinstance(parameter.default_value, dict)

def test_report_filter_creation():
    filter = ReportFilter(
        id=1,
        report_id=1,
        name="Product Category",
        description="Filter by product category",
        field="category",
        operator="equals",
        value="electronics"
    )
    
    assert filter.id == 1
    assert filter.report_id == 1
    assert filter.name == "Product Category"
    assert filter.description == "Filter by product category"
    assert filter.field == "category"
    assert filter.operator == "equals"
    assert filter.value == "electronics"

def test_report_column_creation():
    column = ReportColumn(
        id=1,
        report_id=1,
        name="Total Sales",
        description="Total sales amount",
        field="total_sales",
        type="currency",
        format="USD",
        is_visible=True
    )
    
    assert column.id == 1
    assert column.report_id == 1
    assert column.name == "Total Sales"
    assert column.description == "Total sales amount"
    assert column.field == "total_sales"
    assert column.type == "currency"
    assert column.format == "USD"
    assert column.is_visible is True

def test_report_format_creation():
    format = ReportFormat(
        id=1,
        report_id=1,
        name="PDF Format",
        description="PDF report format",
        type="pdf",
        settings={
            "page_size": "A4",
            "orientation": "portrait",
            "header": True
        },
        is_active=True
    )
    
    assert format.id == 1
    assert format.report_id == 1
    assert format.name == "PDF Format"
    assert format.description == "PDF report format"
    assert format.type == "pdf"
    assert isinstance(format.settings, dict)
    assert format.is_active is True

def test_report_delivery_creation():
    delivery = ReportDelivery(
        id=1,
        report_id=1,
        name="Email Delivery",
        description="Email report delivery",
        type="email",
        recipients=["user@example.com"],
        is_active=True
    )
    
    assert delivery.id == 1
    assert delivery.report_id == 1
    assert delivery.name == "Email Delivery"
    assert delivery.description == "Email report delivery"
    assert delivery.type == "email"
    assert isinstance(delivery.recipients, list)
    assert delivery.is_active is True

def test_report_subscription_creation():
    subscription = ReportSubscription(
        id=1,
        report_id=1,
        user_id=1,
        name="Monthly Subscription",
        description="Monthly report subscription",
        status="active",
        created_at=datetime.now()
    )
    
    assert subscription.id == 1
    assert subscription.report_id == 1
    assert subscription.user_id == 1
    assert subscription.name == "Monthly Subscription"
    assert subscription.description == "Monthly report subscription"
    assert subscription.status == "active"
    assert isinstance(subscription.created_at, datetime)

def test_report_history_creation():
    history = ReportHistory(
        id=1,
        report_id=1,
        user_id=1,
        action="generated",
        details={
            "parameters": {
                "date_range": "2024-01"
            },
            "format": "pdf",
            "size": "2.5MB"
        },
        created_at=datetime.now()
    )
    
    assert history.id == 1
    assert history.report_id == 1
    assert history.user_id == 1
    assert history.action == "generated"
    assert isinstance(history.details, dict)
    assert isinstance(history.created_at, datetime) 