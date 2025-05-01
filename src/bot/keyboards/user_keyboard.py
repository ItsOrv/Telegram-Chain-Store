from telethon import Button
from typing import List, Union
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

def get_user_management_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for user management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🔍 جستجوی کاربر", "user:find"),
            Button.inline("📋 لیست کاربران", "user:list")
        ],
        [
            Button.inline("👤 مدیریت نقش‌ها", "user:roles"),
            Button.inline("🚫 مسدود/فعال‌سازی", "user:ban")
        ],
        [
            Button.inline("« بازگشت به پنل مدیریت", "admin:back")
        ]
    ]

def get_user_settings_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for user settings
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📱 تغییر شماره تماس", "user:change_phone"),
            Button.inline("🔐 تغییر رمز عبور", "user:change_password")
        ],
        [
            Button.inline("🔔 تنظیمات اعلان‌ها", "user:notifications"),
            Button.inline("🌐 زبان", "user:language")
        ],
        [
            Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
        ]
    ]

def get_role_selection_keyboard(user_id: int) -> List[List[Button]]:
    """
    Get the keyboard for role selection
    
    Args:
        user_id: User ID to change role
        
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👑 مدیر", f"set_role:{user_id}:ADMIN"),
            Button.inline("🛒 خریدار", f"set_role:{user_id}:BUYER")
        ],
        [
            Button.inline("🏪 فروشنده", f"set_role:{user_id}:SELLER"),
            Button.inline("💳 کاردار", f"set_role:{user_id}:CARDHOLDER")
        ],
        [
            Button.inline("« بازگشت", "admin:users")
        ]
    ]

def get_user_details_keyboard(user_id: int) -> List[List[Button]]:
    """
    Get the keyboard for user details
    
    Args:
        user_id: User ID
        
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🚫 مسدودسازی", f"manage_user:{user_id}:ban"),
            Button.inline("✅ فعال‌سازی", f"manage_user:{user_id}:unban")
        ],
        [
            Button.inline("👑 تغییر نقش", f"manage_user:{user_id}:promote")
        ],
        [
            Button.inline("« بازگشت", "admin:users")
        ]
    ]

def get_user_keyboard() -> List[List[Button]]:
    """
    Get the main keyboard for regular user (buyer)
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🛒 مشاهده محصولات", "user:browse:products"),
            Button.inline("🛍️ سبد خرید", "user:cart:view")
        ],
        [
            Button.inline("📦 سفارشات من", "user:orders:list"),
            Button.inline("💰 کیف پول", "user:wallet:view")
        ],
        [
            Button.inline("🔍 جستجوی محصول", "user:search:product"),
            Button.inline("🏷️ دسته‌بندی‌ها", "user:browse:categories")
        ],
        [
            Button.inline("👤 پروفایل من", "user:profile:view"),
            Button.inline("📞 پشتیبانی", "user:support")
        ],
        [
            Button.inline("🔔 اعلان‌های من", "user:notifications"),
            Button.inline("📝 راهنما", "user:help")
        ]
    ]

def get_user_cart_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for shopping cart management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👁️ مشاهده سبد خرید", "user:cart:view"),
            Button.inline("💰 پرداخت", "user:cart:checkout")
        ],
        [
            Button.inline("🗑️ خالی کردن سبد", "user:cart:clear"),
            Button.inline("✏️ ویرایش تعداد", "user:cart:edit")
        ],
        [
            Button.inline("🛒 ادامه خرید", "user:browse:products"),
            Button.inline("❤️ ذخیره برای بعد", "user:cart:save")
        ],
        [
            Button.inline("« بازگشت", "user:back")
        ]
    ]

def get_user_orders_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for order management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📦 همه سفارشات", "user:orders:all"),
            Button.inline("🕒 در انتظار پرداخت", "user:orders:pending_payment")
        ],
        [
            Button.inline("🚚 در انتظار تحویل", "user:orders:pending_delivery"),
            Button.inline("✅ تحویل شده", "user:orders:delivered")
        ],
        [
            Button.inline("❌ لغو شده", "user:orders:cancelled"),
            Button.inline("🔍 جستجوی سفارش", "user:orders:search")
        ],
        [
            Button.inline("« بازگشت", "user:back")
        ]
    ]

def get_user_wallet_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for wallet management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("💰 موجودی کیف پول", "user:wallet:balance"),
            Button.inline("➕ افزایش موجودی", "user:wallet:charge")
        ],
        [
            Button.inline("📋 تاریخچه تراکنش‌ها", "user:wallet:history"),
            Button.inline("📊 گزارش مالی", "user:wallet:report")
        ],
        [
            Button.inline("❓ راهنمای کیف پول", "user:wallet:help"),
            Button.inline("🔐 تنظیمات امنیتی", "user:wallet:security")
        ],
        [
            Button.inline("« بازگشت", "user:back")
        ]
    ]

def get_user_profile_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for user profile
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👤 مشاهده پروفایل", "user:profile:view"),
            Button.inline("✏️ ویرایش پروفایل", "user:profile:edit")
        ],
        [
            Button.inline("🏙️ آدرس‌های من", "user:profile:addresses"),
            Button.inline("📱 اطلاعات تماس", "user:profile:contact")
        ],
        [
            Button.inline("🔐 تنظیمات امنیتی", "user:profile:security"),
            Button.inline("🔔 تنظیمات اعلان", "user:profile:notifications")
        ],
        [
            Button.inline("« بازگشت", "user:back")
        ]
    ]

def get_user_delivery_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for delivery management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📍 مشاهده مکان تحویل", "user:delivery:location"),
            Button.inline("🔢 ثبت کد تحویل", "user:delivery:code")
        ],
        [
            Button.inline("📷 مشاهده تصویر محصول", "user:delivery:view_photo"),
            Button.inline("❌ گزارش مشکل", "user:delivery:report")
        ],
        [
            Button.inline("❓ راهنمای تحویل", "user:delivery:help"),
            Button.inline("📞 تماس با پشتیبانی", "user:delivery:support")
        ],
        [
            Button.inline("« بازگشت", "user:orders:back")
        ]
    ]

def get_user_browse_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for browsing products
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🆕 جدیدترین محصولات", "user:browse:new"),
            Button.inline("⭐ محبوب‌ترین محصولات", "user:browse:popular")
        ],
        [
            Button.inline("💲 ارزان‌ترین محصولات", "user:browse:cheapest"),
            Button.inline("🏷️ دسته‌بندی‌ها", "user:browse:categories")
        ],
        [
            Button.inline("🔍 جستجوی پیشرفته", "user:search:advanced"),
            Button.inline("👤 محصولات فروشنده", "user:browse:seller")
        ],
        [
            Button.inline("« بازگشت", "user:back")
        ]
    ]

class UserKeyboards(BaseKeyboard):
    """کلاس مدیریت کیبوردهای کاربر عادی"""
    
    @staticmethod
    def get_user_main_menu() -> List[List[Button]]:
        """دکمه‌های منوی اصلی کاربر"""
        return [
            [
                Button.inline(KeyboardTexts.PRODUCTS, "products"),
                Button.inline(KeyboardTexts.MY_ORDERS, "my_orders")
            ],
            [
                Button.inline(KeyboardTexts.MY_WALLET, "my_wallet"),
                Button.inline(KeyboardTexts.MY_PROFILE, "my_profile")
            ],
            [
                Button.inline(KeyboardTexts.SUPPORT, "support"),
                Button.inline(KeyboardTexts.ABOUT_US, "about_us")
            ]
        ]
    
    @staticmethod
    def get_profile_menu() -> List[List[Button]]:
        """دکمه‌های منوی پروفایل کاربر"""
        return [
            [
                Button.inline(KeyboardTexts.EDIT_PROFILE, "edit_profile"),
                Button.inline(KeyboardTexts.ADDRESSES, "my_addresses")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]
        
    @staticmethod
    def get_wallet_menu() -> List[List[Button]]:
        """دکمه‌های منوی کیف پول کاربر"""
        return [
            [
                Button.inline(KeyboardTexts.CHARGE_WALLET, "charge_wallet"),
                Button.inline(KeyboardTexts.WITHDRAW, "withdraw_money")
            ],
            [
                Button.inline(KeyboardTexts.TRANSACTIONS, "transactions"),
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]

class CartKeyboards:
    """کلاس مدیریت کیبوردهای سبد خرید"""
    
    @staticmethod
    def get_cart_keyboard(cart_empty: bool = False) -> List[List[Button]]:
        """دکمه‌های سبد خرید"""
        if cart_empty:
            return [
                [Button.inline(KeyboardTexts.BROWSE_PRODUCTS, "browse_products")],
                [Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")]
            ]
        
        return [
            [
                Button.inline(KeyboardTexts.CHECKOUT, "checkout"),
                Button.inline(KeyboardTexts.CLEAR_CART, "clear_cart")
            ],
            [
                Button.inline(KeyboardTexts.CONTINUE_SHOPPING, "continue_shopping"),
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]
    
    @staticmethod
    def get_cart_item_actions(item_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات روی آیتم سبد خرید"""
        return [
            [
                Button.inline(KeyboardTexts.INCREASE, f"increase_qty_{item_id}"),
                Button.inline(KeyboardTexts.DECREASE, f"decrease_qty_{item_id}")
            ],
            [
                Button.inline(KeyboardTexts.REMOVE_ITEM, f"remove_item_{item_id}"),
                Button.inline(KeyboardTexts.BACK_TO_CART, "back_to_cart")
            ]
        ]
    
    @staticmethod
    def get_order_confirmation() -> List[List[Button]]:
        """دکمه‌های تأیید سفارش"""
        return [
            [
                Button.inline(KeyboardTexts.CONFIRM_ORDER, "confirm_order"),
                Button.inline(KeyboardTexts.BACK_TO_CART, "back_to_cart")
            ]
        ]

class OrderKeyboards:
    """کلاس مدیریت کیبوردهای سفارشات"""
    
    @staticmethod
    def get_order_history_keyboard() -> List[List[Button]]:
        """دکمه‌های تاریخچه سفارشات"""
        return [
            [
                Button.inline(KeyboardTexts.ACTIVE_ORDERS, "active_orders"),
                Button.inline(KeyboardTexts.COMPLETED_ORDERS, "completed_orders")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]
    
    @staticmethod
    def get_order_details(order_id: str) -> List[List[Button]]:
        """دکمه‌های جزئیات سفارش"""
        return [
            [
                Button.inline(KeyboardTexts.TRACK_ORDER, f"track_order_{order_id}"),
                Button.inline(KeyboardTexts.CANCEL_ORDER, f"cancel_order_{order_id}")
            ],
            [
                Button.inline(KeyboardTexts.CONTACT_SUPPORT, f"order_support_{order_id}"),
                Button.inline(KeyboardTexts.BACK_TO_ORDERS, "back_to_orders")
            ]
        ]
    
    @staticmethod
    def get_delivery_options() -> List[List[Button]]:
        """دکمه‌های انتخاب روش ارسال"""
        return [
            [
                Button.inline(KeyboardTexts.EXPRESS_DELIVERY, "express_delivery"),
                Button.inline(KeyboardTexts.STANDARD_DELIVERY, "standard_delivery")
            ],
            [
                Button.inline(KeyboardTexts.PICKUP, "pickup"),
                Button.inline(KeyboardTexts.BACK_TO_CART, "back_to_cart")
            ]
        ]

class AddressKeyboards:
    """کلاس مدیریت کیبوردهای آدرس"""
    
    @staticmethod
    def get_address_list_keyboard(has_addresses: bool = True) -> List[List[Button]]:
        """دکمه‌های لیست آدرس‌ها"""
        buttons = [
            [Button.inline(KeyboardTexts.ADD_ADDRESS, "add_address")]
        ]
        
        if has_addresses:
            buttons.append([Button.inline(KeyboardTexts.EDIT_ADDRESSES, "edit_addresses")])
        
        buttons.append([Button.inline(KeyboardTexts.BACK_TO_PROFILE, "back_to_profile")])
        return buttons
    
    @staticmethod
    def get_address_actions(address_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات آدرس"""
        return [
            [
                Button.inline(KeyboardTexts.SELECT_ADDRESS, f"select_address_{address_id}"),
                Button.inline(KeyboardTexts.EDIT_ADDRESS, f"edit_address_{address_id}")
            ],
            [
                Button.inline(KeyboardTexts.DELETE_ADDRESS, f"delete_address_{address_id}"),
                Button.inline(KeyboardTexts.BACK_TO_ADDRESSES, "back_to_addresses")
            ]
        ]
    
    @staticmethod
    def get_province_selection() -> List[List[Button]]:
        """دکمه‌های انتخاب استان"""
        # این متد باید از دیتابیس استان‌ها پر شود
        # فعلاً چند نمونه
        return [
            [
                Button.inline("تهران", "province_tehran"),
                Button.inline("اصفهان", "province_isfahan")
            ],
            [
                Button.inline("مشهد", "province_mashhad"),
                Button.inline("شیراز", "province_shiraz")
            ],
            [
                Button.inline("تبریز", "province_tabriz"),
                Button.inline(KeyboardTexts.MORE, "more_provinces")
            ],
            [
                Button.inline(KeyboardTexts.BACK, "back_to_address_form")
            ]
        ]

class NotificationKeyboards:
    """کلاس مدیریت کیبوردهای اعلان‌ها و پیام‌ها"""
    
    @staticmethod
    def get_notification_settings() -> List[List[Button]]:
        """دکمه‌های تنظیمات اعلان‌ها"""
        return [
            [
                Button.inline(KeyboardTexts.ORDER_NOTIFICATIONS, "toggle_order_notif"),
                Button.inline(KeyboardTexts.PROMO_NOTIFICATIONS, "toggle_promo_notif")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_PROFILE, "back_to_profile")
            ]
        ]
    
    @staticmethod
    def get_notification_actions(notif_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات روی اعلان"""
        return [
            [
                Button.inline(KeyboardTexts.MARK_READ, f"mark_read_{notif_id}"),
                Button.inline(KeyboardTexts.DELETE_NOTIFICATION, f"delete_notif_{notif_id}")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_NOTIFICATIONS, "back_to_notifications")
            ]
        ] 