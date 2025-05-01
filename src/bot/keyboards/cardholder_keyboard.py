from telethon import Button
from typing import List

def get_cardholder_keyboard() -> List[List[Button]]:
    """
    Get the main keyboard for the cardholder panel
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("💳 تأیید پرداخت‌ها", "cardholder:payments:verify"),
            Button.inline("💰 تأیید شارژ کیف پول", "cardholder:wallet:verify")
        ],
        [
            Button.inline("📋 پرداخت‌های معلق", "cardholder:payments:pending"),
            Button.inline("📊 گزارش عملکرد", "cardholder:stats")
        ],
        [
            Button.inline("🔔 اعلان‌های سیستم", "cardholder:notifications"),
            Button.inline("❓ راهنمای کارت‌دار", "cardholder:help")
        ],
        [
            Button.inline("👤 پروفایل من", "cardholder:profile"),
            Button.inline("📱 اطلاعات تماس", "cardholder:contact")
        ],
        [
            Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
        ]
    ]

def get_cardholder_payments_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for payment verification
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("✅ تأیید پرداخت", "cardholder:payments:approve"),
            Button.inline("❌ رد پرداخت", "cardholder:payments:reject")
        ],
        [
            Button.inline("📋 لیست پرداخت‌های معلق", "cardholder:payments:pending"),
            Button.inline("🔍 جستجوی پرداخت", "cardholder:payments:search")
        ],
        [
            Button.inline("📊 گزارش پرداخت‌ها", "cardholder:payments:report"),
            Button.inline("🕒 پرداخت‌های اخیر", "cardholder:payments:recent")
        ],
        [
            Button.inline("« بازگشت", "cardholder:back")
        ]
    ]

def get_cardholder_wallet_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for wallet charge verification
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("✅ تأیید شارژ", "cardholder:wallet:approve"),
            Button.inline("❌ رد شارژ", "cardholder:wallet:reject")
        ],
        [
            Button.inline("📋 شارژهای معلق", "cardholder:wallet:pending"),
            Button.inline("🔍 جستجوی شارژ", "cardholder:wallet:search")
        ],
        [
            Button.inline("📊 گزارش شارژها", "cardholder:wallet:report"),
            Button.inline("🕒 شارژهای اخیر", "cardholder:wallet:recent")
        ],
        [
            Button.inline("« بازگشت", "cardholder:back")
        ]
    ]

def get_cardholder_stats_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for cardholder statistics
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📊 آمار کلی", "cardholder:stats:general"),
            Button.inline("💳 آمار تأیید پرداخت", "cardholder:stats:payments")
        ],
        [
            Button.inline("💰 آمار تأیید شارژ", "cardholder:stats:wallet"),
            Button.inline("📆 گزارش روزانه", "cardholder:stats:daily")
        ],
        [
            Button.inline("📈 نمودار عملکرد", "cardholder:stats:chart"),
            Button.inline("⏱️ زمان پاسخگویی", "cardholder:stats:response_time")
        ],
        [
            Button.inline("« بازگشت", "cardholder:back")
        ]
    ]

def get_cardholder_profile_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for cardholder profile
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👤 مشاهده پروفایل", "cardholder:profile:view"),
            Button.inline("✏️ ویرایش پروفایل", "cardholder:profile:edit")
        ],
        [
            Button.inline("🔑 تغییر رمز عبور", "cardholder:profile:change_password"),
            Button.inline("📱 اطلاعات تماس", "cardholder:profile:contact")
        ],
        [
            Button.inline("🔔 تنظیمات اعلان", "cardholder:profile:notifications"),
            Button.inline("📊 عملکرد من", "cardholder:profile:performance")
        ],
        [
            Button.inline("« بازگشت", "cardholder:back")
        ]
    ] 