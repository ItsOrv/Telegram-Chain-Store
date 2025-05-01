from telethon import Button
from typing import List, Union, Optional
from dataclasses import dataclass
from src.core.models import UserRole, User

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

class AdminKeyboards(BaseKeyboard):
    @staticmethod
    def get_users_management() -> List[List[Button]]:
        return BaseKeyboard.create_simple_keyboard(
            [KeyboardTexts.ADMIN_BAN_USER, KeyboardTexts.ADMIN_UNBAN_USER],
            [KeyboardTexts.ADMIN_SUSPEND_USER, KeyboardTexts.ADMIN_UNSUSPEND_USER]
        )

    @staticmethod
    def get_sellers_management(sellers: List[User]) -> List[List[Button]]:
        buttons = [[create_button(
            f"👤 {seller.username or f'Seller_{seller.telegram_id}'}", 
            f"seller_{seller.id}"
        )] for seller in sellers]
        buttons.append([create_button(KeyboardTexts.ADMIN_ADD_SELLER, "add_seller")])
        return BaseKeyboard.add_back_button(buttons)

class RoleKeyboard(BaseKeyboard):
    """Role-based keyboard handler"""
    
    @staticmethod
    def get_keyboard(role: str) -> List[List[Button]]:
        role_layouts = {
            "admin": [
                [(KeyboardTexts.ADMIN_MANAGE_USERS, "manage_users"), 
                 (KeyboardTexts.ADMIN_MANAGE_SELLERS, "manage_sellers")],
                [(KeyboardTexts.ADMIN_MANAGE_CATEGORIES, "manage_categories"), 
                 (KeyboardTexts.ADMIN_MANAGE_PRODUCTS, "manage_products")]
            ],
            "seller": [
                [(KeyboardTexts.SELLER_ADD_PRODUCT, "add_product"), 
                 (KeyboardTexts.SELLER_MY_PRODUCTS, "my_products")],
                [(KeyboardTexts.SELLER_SALES_REPORT, "sales_report"), 
                 (KeyboardTexts.SELLER_NOTIFICATIONS, "notifications")]
            ],
            "customer": [
                [(KeyboardTexts.CUSTOMER_BROWSE, "browse_products"), 
                 (KeyboardTexts.CUSTOMER_CART, "view_cart")],
                [(KeyboardTexts.LOCATION_CHANGE, "change_location"), 
                 (KeyboardTexts.CUSTOMER_ORDERS, "my_orders")]
            ]
        }
        return BaseKeyboard.create_simple_keyboard(*role_layouts.get(role.lower(), []))

class LocationKeyboards:
    @staticmethod
    def get_provinces(provinces) -> List[List[Button]]:
        buttons = [
            [Button.inline(province.name, f"province_{province.id}")]
            for province in provinces
        ]
        buttons.append([Button.inline("🔙 Back", "back_to_main")])
        return buttons

    @staticmethod
    def get_cities(cities) -> List[List[Button]]:
        buttons = [
            [Button.inline(city.name, f"city_{city.id}")]
            for city in cities
        ]
        buttons.append([Button.inline("🔙 Back to Provinces", "back_to_provinces")])
        return buttons

    @staticmethod
    def get_pre_locations(pre_locations, order_id) -> List[List[Button]]:
        buttons = [
            [Button.inline(
                f"{loc.name} - {loc.address[:30]}...",
                f"select_preloc_{order_id}_{loc.id}"
            )] for loc in pre_locations
        ]
        buttons.append([Button.inline("🔙 بازگشت", f"back_to_order_{order_id}")])
        return buttons

class OrderKeyboards:
    @staticmethod
    def get_order_confirmation() -> List[List[Button]]:
        return [
            [Button.inline("✅ تأیید", "confirm_order")],
            [Button.inline("❌ لغو", "cancel_order")]
        ]

    @staticmethod
    def get_payment_methods(total_amount: float, user_balance: float) -> List[List[Button]]:
        buttons = []
        if user_balance >= total_amount:
            buttons.append([Button.inline("💰 پرداخت با موجودی", "pay_with_balance")])
        
        remaining = total_amount - user_balance if user_balance < total_amount else 0
        if remaining > 0:
            buttons.extend([
                [Button.inline("💳 پرداخت با کارت", "pay_remaining_card")],
                [Button.inline("💎 پرداخت با ارز دیجیتال", "pay_remaining_crypto")]
            ])

        buttons.extend([
            [Button.inline("🔙 بازگشت به سبد خرید", "back_to_cart")],
            [Button.inline("❌ انصراف", "cancel_order")]
        ])
        return buttons

    @staticmethod
    def get_checkout_buttons(total_amount: float, user_balance: float) -> List[List[Button]]:
        """دکمه‌های مرحله پرداخت سفارش"""
        buttons = []
        if user_balance >= total_amount:
            buttons.append([Button.inline("💰 پرداخت با موجودی", "pay_with_balance")])
        
        remaining = total_amount - user_balance if user_balance < total_amount else 0
        if remaining > 0:
            buttons.extend([
                [Button.inline("💳 پرداخت با کارت", "pay_remaining_card")],
                [Button.inline("💎 پرداخت با ارز دیجیتال", "pay_remaining_crypto")]
            ])

        buttons.extend([
            [Button.inline("🔙 بازگشت به سبد خرید", "back_to_cart")],
            [Button.inline("❌ انصراف", "cancel_order")]
        ])
        return buttons

    @staticmethod
    def get_order_details_buttons(order_id: int) -> List[List[Button]]:
        """دکمه‌های جزئیات سفارش"""
        return [
            [Button.inline("👁 مشاهده جزئیات", f"view_order_{order_id}")],
            [Button.inline("🔙 بازگشت به لیست سفارش‌ها", "back_to_orders")]
        ]

def get_role_keyboard(role: str) -> List[List[Button]]:
    keyboards = {
        "admin": [
            [
                Button.inline("👤 Manage Users", "manage_users"),
                Button.inline("👥 Manage Sellers", "manage_sellers")
            ],
            [
                Button.inline("📁 Manage Categories", "manage_categories"),
                Button.inline("💾 Get Database", "get_database")
            ]
        ],
        "seller": [
            [
                Button.inline("➕ Add Product", "add_product"),
                Button.inline("📦 My Products", "my_products")
            ],
            [
                Button.inline("📊 Sales Report", "sales_report"),
                Button.inline("🔔 Notifications", "notifications")
            ]
        ],
        "customer": [
            [
                Button.inline("🛍️ Shop", "browse_products"),
                Button.inline("🛒 Cart", "view_cart")
            ],
            [
                Button.inline("📍 Change My Location", "change_location"),
                Button.inline("📦 My Orders", "my_orders")
            ]
        ]
    }
    return keyboards.get(role.lower(), [])

class ProductKeyboards:
    @staticmethod
    def get_product_management() -> List[List[Button]]:
        return [
            [
                Button.inline("➕ Add Product", "add_product"),
                Button.inline("📦 My Products", "my_products")
            ],
            [Button.inline("🔙 Back to Main Menu", "back_to_main")]
        ]

    @staticmethod
    def get_product_options(product_id: int) -> List[List[Button]]:
        return [
            [
                Button.inline("✏️ Edit", f"edit_product_{product_id}"),
                Button.inline("❌ Delete", f"delete_product_{product_id}")
            ],
            [Button.inline("🔙 Back to Products", "back_to_products")]
        ]

class CategoryKeyboards:
    @staticmethod
    def get_categories_list(categories: List) -> List[List[Button]]:
        buttons = [
            [Button.inline(category.name, f"cat_{category.id}")]
            for category in categories
        ]
        buttons.extend([
            [Button.inline("➕ Add New Category", "add_category")],
            [Button.inline("🔙 Back to Main Menu", "back_to_main")]
        ])
        return buttons

    @staticmethod
    def get_category_options(category_id: int) -> List[List[Button]]:
        return [
            [
                Button.inline("✏️ Edit", f"edit_cat_{category_id}"),
                Button.inline("❌ Delete", f"del_cat_{category_id}")
            ],
            [Button.inline("🔙 Back to Categories", "back_to_categories")]
        ]

class NotificationKeyboards:
    @staticmethod
    def get_notification_options() -> List[List[Button]]:
        return [
            [Button.inline("✅ Mark as Read", "mark_read")],
            [Button.inline("🗑 Delete", "delete_notification")],
            [Button.inline("🔙 Back to Notifications", "back_to_notifications")]
        ]

    @staticmethod
    def get_notifications_list(notifications) -> List[List[Button]]:
        buttons = [
            [Button.inline(f"📝 {notif.title[:30]}...", f"notif_{notif.id}")]
            for notif in notifications
        ]
        buttons.append([Button.inline("🔙 Back to Main Menu", "back_to_main")])
        return buttons

class CartKeyboards:
    @staticmethod
    def get_cart_item_options(item_id: int) -> List[List[Button]]:
        return [
            [
                Button.inline("➕ Add One", f"cart_add_{item_id}"),
                Button.inline("➖ Remove One", f"cart_remove_{item_id}")
            ],
            [Button.inline("❌ Delete", f"cart_delete_{item_id}")],
            [Button.inline("🔙 Back to Cart", "back_to_cart")]
        ]

    @staticmethod
    def get_cart_management() -> List[List[Button]]:
        return [
            [Button.inline("💳 Checkout", "checkout")],
            [Button.inline("🗑 Clear Cart", "clear_cart")],
            [Button.inline("🔙 Back to Shopping", "back_to_shopping")]
        ]

class PaymentKeyboards:
    @staticmethod
    def get_crypto_payment_options() -> List[List[Button]]:
        return [
            [
                Button.inline("₿ Bitcoin", "pay_btc"),
                Button.inline("Ξ Ethereum", "pay_eth")
            ],
            [
                Button.inline("⟠ USDT", "pay_usdt"),
                Button.inline("◈ BNB", "pay_bnb")
            ],
            [Button.inline("🔙 Back to Payment Methods", "back_to_payment")]
        ]

    @staticmethod
    def get_payment_verification() -> List[List[Button]]:
        return [
            [Button.inline("✅ Verify Payment", "verify_payment")],
            [Button.inline("❌ Cancel Payment", "cancel_payment")]
        ]

class DialogKeyboards:
    @staticmethod
    def get_back_to_main() -> List[List[Button]]:
        return [[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]

    @staticmethod
    def get_retry_cancel() -> List[List[Button]]:
        return [
            [Button.inline("🔄 تلاش مجدد", "retry")],
            [Button.inline("❌ انصراف", "cancel")]
        ]

class BalanceKeyboards:
    @staticmethod
    def get_charge_options() -> List[List[Button]]:
        return [
            [
                Button.inline("💳 Online Payment", "charge_online"),
                Button.inline("💎 Crypto Payment", "charge_crypto")
            ],
            [Button.inline("🔙 Back to Main Menu", "back_to_main")]
        ]

    @staticmethod 
    def get_charge_amounts() -> List[List[Button]]:
        return [
            [
                Button.inline("💰 10,000", "charge_10000"),
                Button.inline("💰 20,000", "charge_20000")
            ],
            [
                Button.inline("💰 50,000", "charge_50000"),
                Button.inline("💰 100,000", "charge_100000")
            ],
            [Button.inline("💰 Custom Amount", "charge_custom")],
            [Button.inline("🔙 Back", "back_to_charge")]
        ]

class SupportKeyboards:
    @staticmethod
    def get_support_options() -> List[List[Button]]:
        return [
            [
                Button.inline("❓ FAQ", "show_faq"),
                Button.inline("📝 New Ticket", "new_ticket")
            ],
            [Button.inline("📋 My Tickets", "my_tickets")],
            [Button.inline("🔙 Back to Main Menu", "back_to_main")]
        ]

    @staticmethod
    def get_ticket_actions(ticket_id: int) -> List[List[Button]]:
        return [
            [
                Button.inline("✏️ Reply", f"reply_ticket_{ticket_id}"),
                Button.inline("❌ Close", f"close_ticket_{ticket_id}")
            ],
            [Button.inline("🔙 Back to Tickets", "back_to_tickets")]
        ]

class BackKeyboards:
    @staticmethod 
    def get_error_handling() -> List[List[Button]]:
        return [
            [Button.inline("⚠️ خطا در عملیات", "show_error")],
            [Button.inline("🔄 تلاش مجدد", "retry")],
            [Button.inline("🔙 بازگشت", "back")]
        ]

    @staticmethod
    def get_basic_back_button() -> List[List[Button]]:
        return [[Button.inline("🔙 بازگشت", "back")]]

    @staticmethod
    def get_simple_confirmation() -> List[List[Button]]:
        return [
            [
                Button.inline("✅ بله", "yes"),
                Button.inline("❌ خیر", "no")
            ]
        ]


