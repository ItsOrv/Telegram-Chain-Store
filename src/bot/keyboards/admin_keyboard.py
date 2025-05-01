from telethon import Button
from typing import List, Union

from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts, create_button
from src.core.models import UserRole, User

def get_admin_keyboard() -> List[List[Button]]:
    """
    Get the comprehensive keyboard for the admin panel
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👥 مدیریت کاربران", "admin:users"),
            Button.inline("📦 مدیریت محصولات", "admin:products")
        ],
        [
            Button.inline("📍 مدیریت مکان تحویل", "admin:locations"),
            Button.inline("💳 تأیید پرداخت‌ها", "admin:payments")
        ],
        [
            Button.inline("💰 تأیید شارژ کیف پول", "admin:wallet_charges"),
            Button.inline("🔐 مدیریت نقش‌ها", "admin:roles")
        ],
        [
            Button.inline("📊 آمار و گزارش‌ها", "admin:stats"),
            Button.inline("⚙️ تنظیمات سیستم", "admin:settings")
        ],
        [
            Button.inline("🔔 اعلان‌ها", "admin:notifications"),
            Button.inline("❌ کاربران مسدود", "admin:blocked_users")
        ],
        [
            Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
        ]
    ]

def get_admin_users_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for user management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🔍 جستجوی کاربر", "admin:users:search"),
            Button.inline("👤 افزودن فروشنده", "admin:users:add_seller")
        ],
        [
            Button.inline("💳 افزودن کارت‌دار", "admin:users:add_cardholder"),
            Button.inline("👥 لیست کاربران", "admin:users:list")
        ],
        [
            Button.inline("🚫 مسدودسازی", "admin:users:block"),
            Button.inline("✅ رفع مسدودی", "admin:users:unblock")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_products_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for product management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🔍 جستجوی محصول", "admin:products:search"),
            Button.inline("📦 لیست محصولات", "admin:products:list")
        ],
        [
            Button.inline("✅ تأیید محصولات", "admin:products:approve"),
            Button.inline("❌ رد محصولات", "admin:products:reject")
        ],
        [
            Button.inline("🗑️ حذف محصول", "admin:products:delete"),
            Button.inline("🏷️ دسته‌بندی‌ها", "admin:products:categories")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_locations_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for delivery location management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("➕ افزودن مکان جدید", "admin:locations:add"),
            Button.inline("📍 لیست مکان‌ها", "admin:locations:list")
        ],
        [
            Button.inline("🏙️ مدیریت شهرها", "admin:locations:cities"),
            Button.inline("🏘️ مدیریت مناطق", "admin:locations:areas")
        ],
        [
            Button.inline("❌ حذف مکان", "admin:locations:delete"),
            Button.inline("✏️ ویرایش مکان", "admin:locations:edit")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_payments_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for payment management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("✅ تأیید پرداخت‌ها", "admin:payments:approve"),
            Button.inline("❌ رد پرداخت‌ها", "admin:payments:reject")
        ],
        [
            Button.inline("🔄 پرداخت‌های معلق", "admin:payments:pending"),
            Button.inline("💰 شارژهای کیف پول", "admin:payments:wallet_charges")
        ],
        [
            Button.inline("📊 گزارش مالی", "admin:payments:reports"),
            Button.inline("⚙️ تنظیمات پرداخت", "admin:payments:settings")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_settings_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for admin settings
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("🤖 تنظیمات ربات", "admin:settings:bot"),
            Button.inline("💰 تنظیمات مالی", "admin:settings:financial")
        ],
        [
            Button.inline("📱 پیام‌های سیستم", "admin:settings:messages"),
            Button.inline("🛡️ تنظیمات امنیتی", "admin:settings:security")
        ],
        [
            Button.inline("⏱️ زمان‌بندی‌ها", "admin:settings:timers"),
            Button.inline("🌐 تنظیمات زبان", "admin:settings:language")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_stats_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for admin statistics
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📊 آمار کلی", "admin:stats:general"),
            Button.inline("👥 آمار کاربران", "admin:stats:users")
        ],
        [
            Button.inline("📦 آمار محصولات", "admin:stats:products"),
            Button.inline("💰 آمار مالی", "admin:stats:financial")
        ],
        [
            Button.inline("📈 نمودار فروش", "admin:stats:sales_chart"),
            Button.inline("🕒 گزارش زمانی", "admin:stats:time_report")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

def get_admin_roles_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for role management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("👤 مدیریت ادمین‌ها", "admin:roles:admins"),
            Button.inline("💳 مدیریت کارت‌داران", "admin:roles:cardholders")
        ],
        [
            Button.inline("🛒 مدیریت فروشندگان", "admin:roles:sellers"),
            Button.inline("👥 مدیریت کاربران", "admin:roles:users")
        ],
        [
            Button.inline("🔑 مجوزهای دسترسی", "admin:roles:permissions"),
            Button.inline("➕ تعریف نقش جدید", "admin:roles:add")
        ],
        [
            Button.inline("« بازگشت", "admin:back")
        ]
    ]

class AdminKeyboards(BaseKeyboard):
    """کلاس مدیریت کیبوردهای ادمین"""
    
    @staticmethod
    def get_admin_main_menu() -> List[List[Button]]:
        """دکمه‌های منوی اصلی ادمین"""
        return [
            [
                Button.inline(KeyboardTexts.ADMIN_USERS, "admin:users"),
                Button.inline(KeyboardTexts.ADMIN_PRODUCTS, "admin:products")
            ],
            [
                Button.inline(KeyboardTexts.ADMIN_ORDERS, "admin:orders"),
                Button.inline(KeyboardTexts.ADMIN_PAYMENTS, "admin:payments")
            ],
            [
                Button.inline(KeyboardTexts.ADMIN_REPORTS, "admin:reports"),
                Button.inline(KeyboardTexts.ADMIN_SETTINGS, "admin:settings")
            ],
            [
                Button.inline(KeyboardTexts.ADMIN_BROADCAST, "admin:broadcast"),
                Button.inline(KeyboardTexts.EXIT_ADMIN, "exit_admin")
            ]
        ]
    
    @staticmethod
    def get_admin_settings() -> List[List[Button]]:
        """دکمه‌های تنظیمات ادمین"""
        return [
            [
                Button.inline(KeyboardTexts.BOT_SETTINGS, "admin:settings:bot"),
                Button.inline(KeyboardTexts.SHOP_SETTINGS, "admin:settings:shop")
            ],
            [
                Button.inline(KeyboardTexts.PAYMENT_SETTINGS, "admin:settings:payment"),
                Button.inline(KeyboardTexts.SHIPPING_SETTINGS, "admin:settings:shipping")
            ],
            [
                Button.inline(KeyboardTexts.BACKUP_SETTINGS, "admin:settings:backup"),
                Button.inline(KeyboardTexts.BACK, "admin:back")
            ]
        ]
    
    @staticmethod
    def get_admin_confirmation(action: str, item_id: str) -> List[List[Button]]:
        """دکمه‌های تأیید عملیات ادمین"""
        return [
            [
                Button.inline(KeyboardTexts.CONFIRM, f"admin:confirm:{action}:{item_id}"),
                Button.inline(KeyboardTexts.CANCEL, f"admin:cancel:{action}:{item_id}")
            ]
        ]

class UserManagementKeyboards:
    """کلاس مدیریت کیبوردهای مدیریت کاربران"""
    
    @staticmethod
    def get_user_management_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت کاربران"""
        return [
            [
                Button.inline("👥 لیست کاربران", "admin:users:list"),
                Button.inline("🔍 جستجوی کاربر", "admin:users:search")
            ],
            [
                Button.inline("🚫 کاربران مسدود", "admin:users:blocked"),
                Button.inline("⭐ کاربران ویژه", "admin:users:vip")
            ],
            [
                Button.inline("👮 مدیریت دسترسی‌ها", "admin:users:roles"),
                Button.inline("« بازگشت", "admin:back")
            ]
        ]
    
    @staticmethod
    def get_user_actions(user_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات کاربر"""
        return [
            [
                Button.inline("📝 ویرایش اطلاعات", f"admin:users:edit:{user_id}"),
                Button.inline("🛒 سفارشات کاربر", f"admin:users:orders:{user_id}")
            ],
            [
                Button.inline("🔐 تغییر دسترسی", f"admin:users:role:{user_id}"),
                Button.inline("💰 کیف پول کاربر", f"admin:users:wallet:{user_id}")
            ],
            [
                Button.inline("🚫 مسدود کردن", f"admin:users:block:{user_id}"),
                Button.inline("« بازگشت", "admin:users:back")
            ]
        ]
    
    @staticmethod
    def get_user_list_keyboard(page: int = 1, total_pages: int = 1) -> List[List[Button]]:
        """دکمه‌های لیست کاربران"""
        buttons = []
        
        # دکمه‌های صفحه‌بندی
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:users:list:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:users:list:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # دکمه‌های فیلتر
        buttons.append([
            Button.inline("🔍 فیلتر", "admin:users:filter"),
            Button.inline("🔄 بروزرسانی", f"admin:users:refresh:{page}")
        ])
        
        # دکمه بازگشت
        buttons.append([
            Button.inline("« بازگشت", "admin:users:back_to_menu")
        ])
        
        return buttons

class OrderManagementKeyboards:
    """کلاس مدیریت کیبوردهای سفارشات ادمین"""
    
    @staticmethod
    def get_admin_orders_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت سفارشات"""
        return [
            [
                Button.inline("🕒 سفارشات جدید", "admin:orders:new"),
                Button.inline("📦 در حال پردازش", "admin:orders:processing")
            ],
            [
                Button.inline("🚚 در حال ارسال", "admin:orders:shipping"),
                Button.inline("✅ تکمیل شده", "admin:orders:completed")
            ],
            [
                Button.inline("🔍 جستجوی سفارش", "admin:orders:search"),
                Button.inline("« بازگشت", "admin:back")
            ]
        ]
    
    @staticmethod
    def get_order_actions(order_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات سفارش"""
        return [
            [
                Button.inline("📝 ویرایش وضعیت", f"admin:orders:status:{order_id}"),
                Button.inline("🚚 ثبت ارسال", f"admin:orders:ship:{order_id}")
            ],
            [
                Button.inline("❌ لغو سفارش", f"admin:orders:cancel:{order_id}"),
                Button.inline("🖨️ چاپ فاکتور", f"admin:orders:invoice:{order_id}")
            ],
            [
                Button.inline("« بازگشت", "admin:orders:back")
            ]
        ]
    
    @staticmethod
    def get_order_status_options(order_id: str) -> List[List[Button]]:
        """دکمه‌های تغییر وضعیت سفارش"""
        return [
            [
                Button.inline("📥 دریافت شده", f"admin:orders:set_status:{order_id}:received"),
                Button.inline("🔄 در حال پردازش", f"admin:orders:set_status:{order_id}:processing")
            ],
            [
                Button.inline("📦 آماده ارسال", f"admin:orders:set_status:{order_id}:ready"),
                Button.inline("🚚 ارسال شده", f"admin:orders:set_status:{order_id}:shipped")
            ],
            [
                Button.inline("✅ تحویل داده شده", f"admin:orders:set_status:{order_id}:delivered"),
                Button.inline("❌ لغو شده", f"admin:orders:set_status:{order_id}:cancelled")
            ],
            [
                Button.inline("« بازگشت", f"admin:orders:back_to_order:{order_id}")
            ]
        ]

class ReportKeyboards:
    """کلاس مدیریت کیبوردهای گزارشات"""
    
    @staticmethod
    def get_admin_reports_keyboard() -> List[List[Button]]:
        """دکمه‌های گزارشات ادمین"""
        return [
            [
                Button.inline("📊 گزارش فروش", "admin:reports:sales"),
                Button.inline("👥 گزارش کاربران", "admin:reports:users")
            ],
            [
                Button.inline("📈 نمودار فروش", "admin:reports:charts"),
                Button.inline("📦 گزارش محصولات", "admin:reports:products")
            ],
            [
                Button.inline("💰 گزارش مالی", "admin:reports:financial"),
                Button.inline("« بازگشت", "admin:back")
            ]
        ]
    
    @staticmethod
    def get_report_period() -> List[List[Button]]:
        """دکمه‌های انتخاب بازه زمانی گزارش"""
        return [
            [
                Button.inline("📅 امروز", "admin:reports:period:today"),
                Button.inline("📅 هفته جاری", "admin:reports:period:week")
            ],
            [
                Button.inline("📅 ماه جاری", "admin:reports:period:month"),
                Button.inline("📅 سال جاری", "admin:reports:period:year")
            ],
            [
                Button.inline("📅 انتخاب بازه", "admin:reports:period:custom"),
                Button.inline("« بازگشت", "admin:reports:back")
            ]
        ]
    
    @staticmethod
    def get_export_options() -> List[List[Button]]:
        """دکمه‌های خروجی گزارش"""
        return [
            [
                Button.inline("📊 Excel", "admin:reports:export:excel"),
                Button.inline("📄 PDF", "admin:reports:export:pdf")
            ],
            [
                Button.inline("📝 CSV", "admin:reports:export:csv"),
                Button.inline("« بازگشت", "admin:reports:back")
            ]
        ] 