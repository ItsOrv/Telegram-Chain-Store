import pytest
from datetime import datetime
from src.core.models.analytics import (
    Analytics, AnalyticsType, AnalyticsMetric,
    AnalyticsDimension, AnalyticsFilter, AnalyticsReport,
    AnalyticsSchedule, AnalyticsConfig, AnalyticsData,
    AnalyticsExport
)

def test_analytics_creation():
    analytics = Analytics(
        id=1,
        name="Sales Analytics",
        description="Sales performance analytics",
        type="sales",
        status="active",
        created_at=datetime.now()
    )
    
    assert analytics.id == 1
    assert analytics.name == "Sales Analytics"
    assert analytics.description == "Sales performance analytics"
    assert analytics.type == "sales"
    assert analytics.status == "active"
    assert isinstance(analytics.created_at, datetime)

def test_analytics_type_creation():
    analytics_type = AnalyticsType(
        id=1,
        name="Sales Analysis",
        description="Sales data analysis",
        category="business",
        is_active=True
    )
    
    assert analytics_type.id == 1
    assert analytics_type.name == "Sales Analysis"
    assert analytics_type.description == "Sales data analysis"
    assert analytics_type.category == "business"
    assert analytics_type.is_active is True

def test_analytics_metric_creation():
    metric = AnalyticsMetric(
        id=1,
        analytics_id=1,
        name="Total Sales",
        description="Total sales amount",
        type="sum",
        unit="USD",
        is_active=True
    )
    
    assert metric.id == 1
    assert metric.analytics_id == 1
    assert metric.name == "Total Sales"
    assert metric.description == "Total sales amount"
    assert metric.type == "sum"
    assert metric.unit == "USD"
    assert metric.is_active is True

def test_analytics_dimension_creation():
    dimension = AnalyticsDimension(
        id=1,
        analytics_id=1,
        name="Product Category",
        description="Product category dimension",
        type="string",
        format="text",
        is_active=True
    )
    
    assert dimension.id == 1
    assert dimension.analytics_id == 1
    assert dimension.name == "Product Category"
    assert dimension.description == "Product category dimension"
    assert dimension.type == "string"
    assert dimension.format == "text"
    assert dimension.is_active is True

def test_analytics_filter_creation():
    filter = AnalyticsFilter(
        id=1,
        analytics_id=1,
        name="Date Range",
        description="Date range filter",
        type="date_range",
        condition="date >= '2024-01-01' AND date <= '2024-01-31'",
        is_active=True
    )
    
    assert filter.id == 1
    assert filter.analytics_id == 1
    assert filter.name == "Date Range"
    assert filter.description == "Date range filter"
    assert filter.type == "date_range"
    assert filter.condition == "date >= '2024-01-01' AND date <= '2024-01-31'"
    assert filter.is_active is True

def test_analytics_report_creation():
    report = AnalyticsReport(
        id=1,
        analytics_id=1,
        name="Monthly Sales Report",
        description="Monthly sales performance report",
        metrics=["total_sales", "order_count"],
        dimensions=["product_category", "region"],
        filters=["date_range"],
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.analytics_id == 1
    assert report.name == "Monthly Sales Report"
    assert report.description == "Monthly sales performance report"
    assert isinstance(report.metrics, list)
    assert isinstance(report.dimensions, list)
    assert isinstance(report.filters, list)
    assert isinstance(report.created_at, datetime)

def test_analytics_schedule_creation():
    schedule = AnalyticsSchedule(
        id=1,
        report_id=1,
        name="Monthly Schedule",
        description="Monthly report generation",
        frequency="monthly",
        day_of_month=1,
        time="00:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.report_id == 1
    assert schedule.name == "Monthly Schedule"
    assert schedule.description == "Monthly report generation"
    assert schedule.frequency == "monthly"
    assert schedule.day_of_month == 1
    assert schedule.time == "00:00"
    assert schedule.is_active is True

def test_analytics_config_creation():
    config = AnalyticsConfig(
        id=1,
        analytics_id=1,
        name="Data Source Config",
        description="Data source configuration",
        settings={
            "database": "analytics_db",
            "table": "sales_data",
            "refresh_interval": "1h"
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.analytics_id == 1
    assert config.name == "Data Source Config"
    assert config.description == "Data source configuration"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_analytics_data_creation():
    data = AnalyticsData(
        id=1,
        report_id=1,
        data={
            "total_sales": 100000,
            "order_count": 1000,
            "avg_order_value": 100
        },
        created_at=datetime.now()
    )
    
    assert data.id == 1
    assert data.report_id == 1
    assert isinstance(data.data, dict)
    assert isinstance(data.created_at, datetime)

def test_analytics_export_creation():
    export = AnalyticsExport(
        id=1,
        report_id=1,
        name="CSV Export",
        description="Report data export",
        format="csv",
        status="completed",
        file_path="/path/to/export.csv",
        created_at=datetime.now()
    )
    
    assert export.id == 1
    assert export.report_id == 1
    assert export.name == "CSV Export"
    assert export.description == "Report data export"
    assert export.format == "csv"
    assert export.status == "completed"
    assert export.file_path == "/path/to/export.csv"
    assert isinstance(export.created_at, datetime) 