import pytest
import os

def test_simple():
    """تست ساده برای بررسی محیط تست"""
    assert True

def test_environment():
    """تست بررسی متغیرهای محیطی"""
    assert os.environ.get("TESTING") == "true" 