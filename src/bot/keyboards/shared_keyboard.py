from telethon import Button
from typing import List, Union, Optional
from dataclasses import dataclass

@dataclass
class KeyboardTexts:
    """نگهداری متن دکمه‌ها برای پشتیبانی از چند زبان"""
    
    # Common texts
    BACK = "🔙 Back"
    BACK_TO_MAIN = "🏠 Back to Main Menu"
    CONFIRM = "✅ Confirm"
    CANCEL = "❌ Cancel"
    RETRY = "🔄 Try Again"
    YES = "✅ Yes"
    NO = "❌ No"
    
    # Admin section
    ADMIN_MANAGE_CATEGORIES = "📁 Manage Categories"
    ADMIN_MANAGE_SELLERS = "👥 Manage Sellers"
    ADMIN_MANAGE_USERS = "👤 Manage Users"
    ADMIN_MANAGE_PRODUCTS = "🛍 Manage Products"
    ADMIN_IN_PROGRESS_ORDERS = "📦 In Progress Orders"
    ADMIN_GET_DATABASE = "💾 Get Database"
    ADMIN_GET_REPORT = "📊 Get Report"
    ADMIN_PAYMENT_METHODS = "💳 Payment Methods"
    ADMIN_BAN_USER = "🚫 Ban User"
    ADMIN_UNBAN_USER = "✅ Unban User"
    ADMIN_SUSPEND_USER = "⏸ Suspend User"
    ADMIN_UNSUSPEND_USER = "▶️ Unsuspend User"
    ADMIN_ADD_SELLER = "➕ Add New Seller"
    
    # Seller section
    SELLER_ADD_PRODUCT = "➕ Add Product"
    SELLER_MY_PRODUCTS = "📦 My Products"
    SELLER_VIEW_PRODUCTS = "🛍 View Products"
    SELLER_VIEW_ORDERS = "📦 View Orders"
    SELLER_EDIT_PRODUCT = "✏️ Edit"
    SELLER_DELETE_PRODUCT = "❌ Delete"
    SELLER_SALES_REPORT = "📊 Sales Report"
    SELLER_NOTIFICATIONS = "🔔 Notifications"
    
    # Category section
    CATEGORY_ADD_NEW = "➕ Add New Category"
    CATEGORY_EDIT = "✏️ Edit"
    CATEGORY_DELETE = "❌ Delete"
    
    # Cart section
    CART_ADD_ONE = "➕ Add One"
    CART_REMOVE_ONE = "➖ Remove One"
    CART_DELETE = "❌ Delete"
    CART_CHECKOUT = "💳 Checkout"
    CART_CLEAR = "🗑 Clear Cart"
    
    # Payment section
    PAYMENT_BALANCE = "💰 Pay with Balance"
    PAYMENT_CARD = "💳 Pay with Card"
    PAYMENT_CRYPTO = "💎 Pay with Crypto"
    PAYMENT_VERIFY = "✅ Verify Payment"
    PAYMENT_BTC = "₿ Bitcoin"
    PAYMENT_ETH = "Ξ Ethereum"
    PAYMENT_USDT = "⟠ USDT"
    PAYMENT_BNB = "◈ BNB"
    
    # Location section
    LOCATION_CHANGE = "📍 Change Location"
    LOCATION_CONFIRM = "✅ Confirm Location"
    
    # Support section
    SUPPORT_FAQ = "❓ FAQ"
    SUPPORT_NEW_TICKET = "📝 New Ticket"
    SUPPORT_MY_TICKETS = "📋 My Tickets"
    SUPPORT_REPLY = "✏️ Reply"
    SUPPORT_CLOSE = "❌ Close"
    
    # Notification section
    NOTIF_MARK_READ = "✅ Mark as Read"
    NOTIF_DELETE = "🗑 Delete"

def create_button(text: str, callback_data: str = None) -> Button:
    """Create a single inline button with optional custom callback data"""
    return Button.inline(text, callback_data or text)

def create_keyboard_row(*buttons: Union[str, tuple]) -> List[Button]:
    """Create a row of buttons"""
    row = []
    for button in buttons:
        if isinstance(button, str):
            # Simple text button
            row.append(Button.inline(button))
        elif isinstance(button, tuple):
            # Button with custom callback
            text, callback = button
            row.append(Button.inline(text, callback))
    return row

class BaseKeyboard:
    """Base class for all keyboard classes"""
    
    @staticmethod
    def add_back_button(buttons: List[List[Button]], back_text: str = KeyboardTexts.BACK_TO_MAIN) -> List[List[Button]]:
        """Add a back button to existing keyboard"""
        buttons.append([create_button(back_text)])
        return buttons

    @staticmethod
    def create_simple_keyboard(*rows: List[Union[str, tuple]], include_back: bool = True, back_text: str = KeyboardTexts.BACK_TO_MAIN) -> List[List[Button]]:
        """Create a keyboard from rows of button texts or (text, callback) tuples"""
        keyboard = [create_keyboard_row(*row) for row in rows]
        if include_back:
            BaseKeyboard.add_back_button(keyboard, back_text)
        return keyboard

class BackKeyboards:
    @staticmethod 
    def get_error_handling() -> List[List[Button]]:
        """دکمه‌های مدیریت خطا"""
        return [
            [Button.inline(KeyboardTexts.RETRY, "retry")],
            [Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")]
        ]

    @staticmethod
    def get_basic_back_button() -> List[List[Button]]:
        """دکمه بازگشت ساده"""
        return [[Button.inline(KeyboardTexts.BACK, "back")]]

    @staticmethod
    def get_simple_confirmation() -> List[List[Button]]:
        """دکمه‌های تأیید/لغو ساده"""
        return [
            [Button.inline(KeyboardTexts.CONFIRM, "confirm"), 
             Button.inline(KeyboardTexts.CANCEL, "cancel")]
        ]

class DialogKeyboards:
    @staticmethod
    def get_back_to_main() -> List[List[Button]]:
        """دکمه بازگشت به منوی اصلی"""
        return [[Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")]]

    @staticmethod
    def get_retry_cancel() -> List[List[Button]]:
        """دکمه‌های تلاش مجدد و لغو"""
        return [
            [Button.inline(KeyboardTexts.RETRY, "retry")],
            [Button.inline(KeyboardTexts.CANCEL, "cancel")]
        ] 