from telethon import Button
from typing import List

def get_seller_keyboard() -> List[List[Button]]:
    """
    Get the main keyboard for the seller panel
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("➕ افزودن محصول جدید", "seller:product:add"),
            Button.inline("📦 محصولات من", "seller:products:list")
        ],
        [
            Button.inline("📋 سفارشات جدید", "seller:orders:new"),
            Button.inline("🚚 تحویل‌های در انتظار", "seller:orders:pending")
        ],
        [
            Button.inline("💰 گزارش درآمد", "seller:earnings"),
            Button.inline("🔔 پیام‌های سیستم", "seller:notifications")
        ],
        [
            Button.inline("📊 آمار فروش", "seller:stats"),
            Button.inline("❓ راهنمای فروشنده", "seller:help")
        ],
        [
            Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
        ]
    ]

def get_seller_products_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller's product management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("➕ افزودن محصول", "seller:product:add"),
            Button.inline("📦 لیست محصولات", "seller:products:list")
        ],
        [
            Button.inline("✏️ ویرایش محصول", "seller:product:edit"),
            Button.inline("🗑️ حذف محصول", "seller:product:delete")
        ],
        [
            Button.inline("🏷️ دسته‌بندی محصولات", "seller:products:categories"),
            Button.inline("📷 مدیریت تصاویر", "seller:products:images")
        ],
        [
            Button.inline("✅ محصولات تأیید شده", "seller:products:approved"),
            Button.inline("⏳ محصولات در انتظار", "seller:products:pending")
        ],
        [
            Button.inline("❌ محصولات رد شده", "seller:products:rejected"),
            Button.inline("❓ راهنمای افزودن محصول", "seller:products:help")
        ],
        [
            Button.inline("« بازگشت", "seller:back")
        ]
    ]

def get_seller_orders_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller's order management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📋 سفارشات جدید", "seller:orders:new"),
            Button.inline("🚚 در انتظار تحویل", "seller:orders:pending")
        ],
        [
            Button.inline("✅ تحویل داده شده", "seller:orders:delivered"),
            Button.inline("❌ لغو شده", "seller:orders:cancelled")
        ],
        [
            Button.inline("🔍 جستجوی سفارش", "seller:orders:search"),
            Button.inline("📊 آمار سفارشات", "seller:orders:stats")
        ],
        [
            Button.inline("« بازگشت", "seller:back")
        ]
    ]

def get_seller_delivery_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller's delivery management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📍 مشاهده مکان تحویل", "seller:delivery:location"),
            Button.inline("📷 ارسال تصویر تحویل", "seller:delivery:upload_photo")
        ],
        [
            Button.inline("🔢 ثبت کد تحویل", "seller:delivery:code"),
            Button.inline("⏰ تمدید زمان تحویل", "seller:delivery:extend_time")
        ],
        [
            Button.inline("❓ راهنمای تحویل", "seller:delivery:help"),
            Button.inline("❌ گزارش مشکل", "seller:delivery:report")
        ],
        [
            Button.inline("« بازگشت", "seller:orders:back")
        ]
    ]

def get_seller_earnings_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller's earnings management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("💰 کل درآمد", "seller:earnings:total"),
            Button.inline("💸 درآمد قابل برداشت", "seller:earnings:available")
        ],
        [
            Button.inline("🔄 درخواست برداشت", "seller:earnings:withdraw"),
            Button.inline("📊 آمار فروش", "seller:earnings:stats")
        ],
        [
            Button.inline("📆 گزارش ماهانه", "seller:earnings:monthly"),
            Button.inline("📋 سوابق برداشت", "seller:earnings:history")
        ],
        [
            Button.inline("« بازگشت", "seller:back")
        ]
    ]

def get_seller_stats_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for seller's statistics
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("📈 آمار کلی", "seller:stats:general"),
            Button.inline("📦 آمار محصولات", "seller:stats:products")
        ],
        [
            Button.inline("💰 آمار مالی", "seller:stats:earnings"),
            Button.inline("👥 آمار مشتریان", "seller:stats:customers")
        ],
        [
            Button.inline("📊 نمودار فروش", "seller:stats:chart"),
            Button.inline("📆 گزارش زمانی", "seller:stats:time")
        ],
        [
            Button.inline("« بازگشت", "seller:back")
        ]
    ] 