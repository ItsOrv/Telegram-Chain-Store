from telethon import Button
from typing import List

def get_profile_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for the profile command
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("💰 کیف پول من", "profile:wallet"),
            Button.inline("📦 سفارشات من", "profile:orders")
        ],
        [
            Button.inline("🔄 تغییر نقش", "profile:change_role"),
            Button.inline("⚙️ تنظیمات", "profile:settings")
        ],
        [
            Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
        ]
    ]

def get_edit_profile_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for editing profile
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("✏️ تغییر نام", "edit_profile:name"),
            Button.inline("📱 تغییر شماره تماس", "edit_profile:phone")
        ],
        [
            Button.inline("📧 تغییر ایمیل", "edit_profile:email"),
            Button.inline("🔐 تغییر رمز عبور", "edit_profile:password")
        ],
        [
            Button.inline("« بازگشت", "profile:back")
        ]
    ]

def get_wallet_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for wallet management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("💵 افزایش موجودی", "wallet:add_funds"),
            Button.inline("📊 تاریخچه تراکنش‌ها", "wallet:history")
        ],
        [
            Button.inline("💸 برداشت", "wallet:withdraw")
        ],
        [
            Button.inline("« بازگشت", "profile:back")
        ]
    ]

def get_wallet_history_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for wallet history
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("« بازگشت به کیف پول", "wallet:back")
        ]
    ]

def get_back_to_wallet_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for going back to wallet
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("« بازگشت به کیف پول", "wallet:back")
        ]
    ]

def get_language_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for language selection
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🇮🇷 فارسی", "language:fa"),
            Button.inline("🇬🇧 English", "language:en")
        ],
        [
            Button.inline("« بازگشت", "profile:back")
        ]
    ]

def get_cancel_edit_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for canceling edit operation
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("❌ لغو", "profile:back")
        ]
    ] 