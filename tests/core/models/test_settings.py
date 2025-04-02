import pytest
from datetime import datetime
from src.core.models.settings import (
    Settings, SettingsGroup, SettingsValue,
    SettingsHistory, SettingsValidation,
    SettingsMigration, SettingsBackup,
    SettingsImport, SettingsExport
)

def test_settings_creation():
    settings = Settings(
        id=1,
        group_id=1,
        key="store_name",
        value="My Store",
        description="Store name",
        is_system=False,
        is_public=True,
        created_at=datetime.now()
    )
    
    assert settings.id == 1
    assert settings.group_id == 1
    assert settings.key == "store_name"
    assert settings.value == "My Store"
    assert settings.description == "Store name"
    assert settings.is_system is False
    assert settings.is_public is True
    assert isinstance(settings.created_at, datetime)

def test_settings_group_creation():
    group = SettingsGroup(
        id=1,
        name="general",
        description="General settings",
        is_system=False,
        is_public=True,
        order=1
    )
    
    assert group.id == 1
    assert group.name == "general"
    assert group.description == "General settings"
    assert group.is_system is False
    assert group.is_public is True
    assert group.order == 1

def test_settings_value_creation():
    value = SettingsValue(
        id=1,
        settings_id=1,
        value="My Store",
        created_by=100,
        created_at=datetime.now()
    )
    
    assert value.id == 1
    assert value.settings_id == 1
    assert value.value == "My Store"
    assert value.created_by == 100
    assert isinstance(value.created_at, datetime)

def test_settings_history_creation():
    history = SettingsHistory(
        id=1,
        settings_id=1,
        old_value="Old Store",
        new_value="New Store",
        changed_by=100,
        changed_at=datetime.now()
    )
    
    assert history.id == 1
    assert history.settings_id == 1
    assert history.old_value == "Old Store"
    assert history.new_value == "New Store"
    assert history.changed_by == 100
    assert isinstance(history.changed_at, datetime)

def test_settings_validation_creation():
    validation = SettingsValidation(
        id=1,
        settings_id=1,
        rule_type="required",
        rule_value="true",
        error_message="This field is required",
        is_active=True
    )
    
    assert validation.id == 1
    assert validation.settings_id == 1
    assert validation.rule_type == "required"
    assert validation.rule_value == "true"
    assert validation.error_message == "This field is required"
    assert validation.is_active is True

def test_settings_migration_creation():
    migration = SettingsMigration(
        id=1,
        version="1.0.0",
        description="Initial settings migration",
        executed_at=datetime.now(),
        status="completed"
    )
    
    assert migration.id == 1
    assert migration.version == "1.0.0"
    assert migration.description == "Initial settings migration"
    assert isinstance(migration.executed_at, datetime)
    assert migration.status == "completed"

def test_settings_backup_creation():
    backup = SettingsBackup(
        id=1,
        name="Daily Backup",
        description="Daily settings backup",
        data={
            "general": {
                "store_name": "My Store",
                "store_description": "My Store Description"
            }
        },
        created_at=datetime.now()
    )
    
    assert backup.id == 1
    assert backup.name == "Daily Backup"
    assert backup.description == "Daily settings backup"
    assert isinstance(backup.data, dict)
    assert isinstance(backup.created_at, datetime)

def test_settings_import_creation():
    import_settings = SettingsImport(
        id=1,
        name="Import Settings",
        description="Import settings from file",
        file_path="/path/to/settings.json",
        status="pending",
        created_at=datetime.now()
    )
    
    assert import_settings.id == 1
    assert import_settings.name == "Import Settings"
    assert import_settings.description == "Import settings from file"
    assert import_settings.file_path == "/path/to/settings.json"
    assert import_settings.status == "pending"
    assert isinstance(import_settings.created_at, datetime)

def test_settings_export_creation():
    export = SettingsExport(
        id=1,
        name="Export Settings",
        description="Export settings to file",
        file_path="/path/to/export.json",
        format="json",
        status="completed",
        created_at=datetime.now()
    )
    
    assert export.id == 1
    assert export.name == "Export Settings"
    assert export.description == "Export settings to file"
    assert export.file_path == "/path/to/export.json"
    assert export.format == "json"
    assert export.status == "completed"
    assert isinstance(export.created_at, datetime) 