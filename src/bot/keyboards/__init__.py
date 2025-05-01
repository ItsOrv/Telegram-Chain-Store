"""
Keyboards package for all Telegram bot keyboards
"""

# مشترک
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

# کیبوردهای ادمین
from src.bot.keyboards.admin_keyboard import (
    AdminKeyboards, 
    UserManagementKeyboards, 
    OrderManagementKeyboards, 
    ReportKeyboards
)

# کیبوردهای کاربر
from src.bot.keyboards.user_keyboard import (
    UserKeyboards, 
    CartKeyboards, 
    OrderKeyboards,
    AddressKeyboards, 
    NotificationKeyboards
)

# کیبوردهای فروشنده
from src.bot.keyboards.seller_keyboard import SellerKeyboards

# کیبوردهای دارنده کارت
from src.bot.keyboards.cardholder_keyboard import CardholderKeyboards

# کیبوردهای اصلی
from src.bot.keyboards.main_keyboard import MainKeyboards

# کیبوردهای محصولات
from src.bot.keyboards.product_keyboard import (
    ProductKeyboards, 
    CategoryKeyboards
)

# کیبوردهای پرداخت
from src.bot.keyboards.payment_keyboard import (
    PaymentKeyboards, 
    CardholderPaymentKeyboards, 
    AdminPaymentKeyboards, 
    BalanceKeyboards,
    SupportKeyboards
)

# کیبوردهای مکان‌ها
from src.bot.keyboards.locations_keyboard import LocationKeyboards 