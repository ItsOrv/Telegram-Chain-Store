from telethon import Button
from typing import List

from src.bot.keyboards.user_keyboard import get_user_keyboard
from src.bot.keyboards.admin_keyboard import get_admin_keyboard
from src.bot.keyboards.seller_keyboard import get_seller_keyboard
from src.bot.keyboards.cardholder_keyboard import get_cardholder_keyboard

def get_start_keyboard() -> List[List[Button]]:
    """
    Get the main keyboard for the start command (directs to user keyboard)
    
    Returns:
        List of button rows
    """
    return get_user_keyboard()

def get_admin_start_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for admin users (directs to admin keyboard)
    
    Returns:
        List of button rows
    """
    return get_admin_keyboard()

def get_seller_start_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller users (directs to seller keyboard)
    
    Returns:
        List of button rows
    """
    return get_seller_keyboard()

def get_cardholder_start_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for cardholder users (directs to cardholder keyboard)
    
    Returns:
        List of button rows
    """
    return get_cardholder_keyboard()

def get_role_selection_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for role selection
    (for users with multiple roles)
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👤 کاربر عادی", "role:user"),
            Button.inline("👮 ادمین", "role:admin")
        ],
        [
            Button.inline("🛒 فروشنده", "role:seller"),
            Button.inline("💳 کارت‌دار", "role:cardholder")
        ]
    ]

def get_login_register_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for login/register
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👤 ورود به حساب", "auth:login"),
            Button.inline("📝 ثبت‌نام", "auth:register")
        ],
        [
            Button.inline("❓ راهنما", "info:help"),
            Button.inline("📞 پشتیبانی", "info:support")
        ]
    ] 