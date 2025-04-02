import pytest
from datetime import datetime
from src.core.models.optimization import (
    Optimization, OptimizationType, OptimizationTarget,
    OptimizationConfig, OptimizationLog, OptimizationStatus,
    OptimizationMetric, OptimizationReport, OptimizationSchedule,
    OptimizationResult
)

def test_optimization_creation():
    optimization = Optimization(
        id=1,
        name="Performance Optimization",
        description="System performance optimization",
        type="performance",
        status="completed",
        created_at=datetime.now()
    )
    
    assert optimization.id == 1
    assert optimization.name == "Performance Optimization"
    assert optimization.description == "System performance optimization"
    assert optimization.type == "performance"
    assert optimization.status == "completed"
    assert isinstance(optimization.created_at, datetime)

def test_optimization_type_creation():
    optimization_type = OptimizationType(
        id=1,
        name="Database Optimization",
        description="Database performance optimization",
        category="performance",
        is_active=True
    )
    
    assert optimization_type.id == 1
    assert optimization_type.name == "Database Optimization"
    assert optimization_type.description == "Database performance optimization"
    assert optimization_type.category == "performance"
    assert optimization_type.is_active is True

def test_optimization_target_creation():
    target = OptimizationTarget(
        id=1,
        optimization_id=1,
        name="Query Performance",
        description="Database query optimization",
        type="database",
        priority=1
    )
    
    assert target.id == 1
    assert target.optimization_id == 1
    assert target.name == "Query Performance"
    assert target.description == "Database query optimization"
    assert target.type == "database"
    assert target.priority == 1

def test_optimization_config_creation():
    config = OptimizationConfig(
        id=1,
        optimization_id=1,
        name="Cache Config",
        description="Cache optimization settings",
        settings={
            "cache_size": "1GB",
            "ttl": 3600,
            "strategy": "lru"
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.optimization_id == 1
    assert config.name == "Cache Config"
    assert config.description == "Cache optimization settings"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_optimization_log_creation():
    log = OptimizationLog(
        id=1,
        optimization_id=1,
        status="completed",
        message="Optimization completed successfully",
        details={
            "improvement": "25%",
            "duration": "30m",
            "changes": 100
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.optimization_id == 1
    assert log.status == "completed"
    assert log.message == "Optimization completed successfully"
    assert isinstance(log.details, dict)
    assert isinstance(log.created_at, datetime)

def test_optimization_status_creation():
    status = OptimizationStatus(
        id=1,
        optimization_id=1,
        status="in_progress",
        progress=75,
        message="Optimization in progress",
        timestamp=datetime.now()
    )
    
    assert status.id == 1
    assert status.optimization_id == 1
    assert status.status == "in_progress"
    assert status.progress == 75
    assert status.message == "Optimization in progress"
    assert isinstance(status.timestamp, datetime)

def test_optimization_metric_creation():
    metric = OptimizationMetric(
        id=1,
        optimization_id=1,
        name="Response Time",
        description="API response time metric",
        value=150,
        unit="ms",
        timestamp=datetime.now()
    )
    
    assert metric.id == 1
    assert metric.optimization_id == 1
    assert metric.name == "Response Time"
    assert metric.description == "API response time metric"
    assert metric.value == 150
    assert metric.unit == "ms"
    assert isinstance(metric.timestamp, datetime)

def test_optimization_report_creation():
    report = OptimizationReport(
        id=1,
        optimization_id=1,
        name="Performance Report",
        description="System performance report",
        type="summary",
        status="generated",
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.optimization_id == 1
    assert report.name == "Performance Report"
    assert report.description == "System performance report"
    assert report.type == "summary"
    assert report.status == "generated"
    assert isinstance(report.created_at, datetime)

def test_optimization_schedule_creation():
    schedule = OptimizationSchedule(
        id=1,
        optimization_id=1,
        name="Weekly Schedule",
        description="Weekly optimization schedule",
        frequency="weekly",
        day_of_week="monday",
        time="02:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.optimization_id == 1
    assert schedule.name == "Weekly Schedule"
    assert schedule.description == "Weekly optimization schedule"
    assert schedule.frequency == "weekly"
    assert schedule.day_of_week == "monday"
    assert schedule.time == "02:00"
    assert schedule.is_active is True

def test_optimization_result_creation():
    result = OptimizationResult(
        id=1,
        optimization_id=1,
        name="Query Optimization",
        description="Database query optimization results",
        improvement="25%",
        details={
            "before": "500ms",
            "after": "375ms",
            "queries": 1000
        },
        created_at=datetime.now()
    )
    
    assert result.id == 1
    assert result.optimization_id == 1
    assert result.name == "Query Optimization"
    assert result.description == "Database query optimization results"
    assert result.improvement == "25%"
    assert isinstance(result.details, dict)
    assert isinstance(result.created_at, datetime) 