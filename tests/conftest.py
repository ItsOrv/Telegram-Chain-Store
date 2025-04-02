import pytest
import os
import sys
from pathlib import Path

# اضافه کردن مسیر src به PYTHONPATH
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

# تنظیمات محیط تست
os.environ["TESTING"] = "true"

def pytest_configure(config):
    """تنظیمات pytest قبل از اجرای تست‌ها"""
    # غیرفعال کردن pytest-twisted
    config.option.no_twisted = True

@pytest.fixture(autouse=True)
def setup_test_env():
    """تنظیم محیط تست قبل از هر تست"""
    # اینجا می‌توانید تنظیمات اضافی محیط تست را اضافه کنید
    yield
    # پاکسازی بعد از هر تست
    pass 