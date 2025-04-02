import pytest
from datetime import datetime
from src.core.models.security import (
    Security, SecurityPolicy, SecurityRule,
    SecurityLog, SecurityAlert, SecurityScan,
    SecurityConfig, SecurityReport, SecurityAudit,
    SecurityIncident
)

def test_security_creation():
    security = Security(
        id=1,
        name="Main Security",
        description="Main security configuration",
        status="active",
        created_at=datetime.now()
    )
    
    assert security.id == 1
    assert security.name == "Main Security"
    assert security.description == "Main security configuration"
    assert security.status == "active"
    assert isinstance(security.created_at, datetime)

def test_security_policy_creation():
    policy = SecurityPolicy(
        id=1,
        security_id=1,
        name="Password Policy",
        description="Password requirements policy",
        type="authentication",
        is_active=True
    )
    
    assert policy.id == 1
    assert policy.security_id == 1
    assert policy.name == "Password Policy"
    assert policy.description == "Password requirements policy"
    assert policy.type == "authentication"
    assert policy.is_active is True

def test_security_rule_creation():
    rule = SecurityRule(
        id=1,
        policy_id=1,
        name="Password Length",
        description="Minimum password length rule",
        condition="length >= 8",
        action="reject",
        priority=1
    )
    
    assert rule.id == 1
    assert rule.policy_id == 1
    assert rule.name == "Password Length"
    assert rule.description == "Minimum password length rule"
    assert rule.condition == "length >= 8"
    assert rule.action == "reject"
    assert rule.priority == 1

def test_security_log_creation():
    log = SecurityLog(
        id=1,
        security_id=1,
        type="login_attempt",
        status="failed",
        details={
            "ip": "192.168.1.1",
            "user": "test_user"
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.security_id == 1
    assert log.type == "login_attempt"
    assert log.status == "failed"
    assert isinstance(log.details, dict)
    assert isinstance(log.created_at, datetime)

def test_security_alert_creation():
    alert = SecurityAlert(
        id=1,
        security_id=1,
        name="Suspicious Activity",
        description="Multiple failed login attempts",
        severity="high",
        status="open",
        created_at=datetime.now()
    )
    
    assert alert.id == 1
    assert alert.security_id == 1
    assert alert.name == "Suspicious Activity"
    assert alert.description == "Multiple failed login attempts"
    assert alert.severity == "high"
    assert alert.status == "open"
    assert isinstance(alert.created_at, datetime)

def test_security_scan_creation():
    scan = SecurityScan(
        id=1,
        security_id=1,
        name="Vulnerability Scan",
        description="System vulnerability scan",
        type="automated",
        status="completed",
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    
    assert scan.id == 1
    assert scan.security_id == 1
    assert scan.name == "Vulnerability Scan"
    assert scan.description == "System vulnerability scan"
    assert scan.type == "automated"
    assert scan.status == "completed"
    assert isinstance(scan.started_at, datetime)
    assert isinstance(scan.completed_at, datetime)

def test_security_config_creation():
    config = SecurityConfig(
        id=1,
        security_id=1,
        name="Firewall Config",
        description="Firewall configuration",
        settings={
            "enabled": True,
            "ports": [80, 443],
            "rules": []
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.security_id == 1
    assert config.name == "Firewall Config"
    assert config.description == "Firewall configuration"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_security_report_creation():
    report = SecurityReport(
        id=1,
        security_id=1,
        name="Monthly Security Report",
        description="Monthly security assessment",
        type="compliance",
        status="generated",
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.security_id == 1
    assert report.name == "Monthly Security Report"
    assert report.description == "Monthly security assessment"
    assert report.type == "compliance"
    assert report.status == "generated"
    assert isinstance(report.created_at, datetime)

def test_security_audit_creation():
    audit = SecurityAudit(
        id=1,
        security_id=1,
        name="Access Audit",
        description="User access audit",
        type="access",
        status="completed",
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    
    assert audit.id == 1
    assert audit.security_id == 1
    assert audit.name == "Access Audit"
    assert audit.description == "User access audit"
    assert audit.type == "access"
    assert audit.status == "completed"
    assert isinstance(audit.started_at, datetime)
    assert isinstance(audit.completed_at, datetime)

def test_security_incident_creation():
    incident = SecurityIncident(
        id=1,
        security_id=1,
        name="Data Breach",
        description="Suspected data breach incident",
        severity="critical",
        status="investigating",
        created_at=datetime.now()
    )
    
    assert incident.id == 1
    assert incident.security_id == 1
    assert incident.name == "Data Breach"
    assert incident.description == "Suspected data breach incident"
    assert incident.severity == "critical"
    assert incident.status == "investigating"
    assert isinstance(incident.created_at, datetime) 