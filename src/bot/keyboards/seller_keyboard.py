from telethon import Button
from typing import List, Optional, Dict, Any, Union
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

class SellerKeyboards(BaseKeyboard):
    """کلاس مدیریت کیبوردهای فروشنده"""
    
    @staticmethod
    def get_seller_main_menu() -> List[List[Button]]:
        """دکمه‌های منوی اصلی فروشنده"""
        return [
            [
                Button.inline("📦 مدیریت محصولات", "seller:products"),
                Button.inline("🛒 سفارشات در جریان", "seller:orders:in_progress")
            ],
            [
                Button.inline("💳 مدیریت پرداخت", "seller:payment"),
                Button.inline("📊 گزارش‌ها", "seller:reports")
            ],
            [
                Button.inline("🏷️ درخواست دسته‌بندی", "seller:category:request"),
                Button.inline("👤 پروفایل", "seller:profile")
            ],
            [
                Button.inline("🔙 بازگشت به منوی اصلی", "back_to_main")
            ]
        ]
    
    @staticmethod
    def get_seller_products_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت محصولات فروشنده"""
        return [
            [
                Button.inline("➕ افزودن محصول", "seller:products:add"),
                Button.inline("📋 لیست محصولات", "seller:products:list")
            ],
            [
                Button.inline("🔍 جستجوی محصول", "seller:products:search"),
                Button.inline("📦 مدیریت موجودی", "seller:products:stock")
            ],
            [
                Button.inline("🏷️ دسته‌بندی‌ها", "seller:products:categories"),
                Button.inline("« بازگشت", "seller:back")
            ]
        ]
    
    @staticmethod
    def get_seller_product_actions(product_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات محصول فروشنده"""
        return [
            [
                Button.inline("✏️ ویرایش محصول", f"seller:products:edit:{product_id}"),
                Button.inline("❌ حذف محصول", f"seller:products:delete:{product_id}")
            ],
            [
                Button.inline("📦 تغییر موجودی", f"seller:products:stock:{product_id}"),
                Button.inline("💲 تغییر قیمت", f"seller:products:price:{product_id}")
            ],
            [
                Button.inline("🖼️ مدیریت تصاویر", f"seller:products:images:{product_id}"),
                Button.inline("« بازگشت", "seller:products:back")
            ]
        ]
    
    @staticmethod
    def get_seller_product_list(products: List, page: int = 1, total_pages: int = 1) -> List[List[Button]]:
        """دکمه‌های لیست محصولات فروشنده با نمایش دکمه‌های عملیات برای هر محصول"""
        buttons = []
        
        for product in products:
            product_id = product.id
            product_name = product.name
            
            # دکمه اصلی محصول
            buttons.append([Button.inline(f"📦 {product_name}", f"seller:products:view:{product_id}")])
            # دکمه‌های عملیات محصول
            buttons.append([
                Button.inline("✏️ ویرایش", f"seller:products:edit:{product_id}"),
                Button.inline("❌ حذف", f"seller:products:delete:{product_id}"),
                Button.inline("📦 موجودی", f"seller:products:stock:{product_id}")
            ])
        
        # دکمه‌های صفحه‌بندی
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"seller:products:list:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"seller:products:list:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
        
        # دکمه افزودن محصول جدید
        buttons.append([Button.inline("➕ افزودن محصول", "seller:products:add")])
        buttons.append([Button.inline("« بازگشت", "seller:back")])
        
        return buttons
    
    @staticmethod
    def get_seller_orders_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت سفارشات فروشنده"""
        return [
            [
                Button.inline("🆕 سفارشات جدید", "seller:orders:new"),
                Button.inline("🔄 در حال پردازش", "seller:orders:processing")
            ],
            [
                Button.inline("🚚 ارسال شده", "seller:orders:shipped"),
                Button.inline("✅ تکمیل شده", "seller:orders:completed")
            ],
            [
                Button.inline("❌ لغو شده", "seller:orders:cancelled"),
                Button.inline("« بازگشت", "seller:back")
            ]
        ]
    
    @staticmethod
    def get_seller_order_actions(order_id: str) -> List[List[Button]]:
        """دکمه‌های عملیات سفارش فروشنده"""
        return [
            [
                Button.inline("✅ تأیید سفارش", f"seller:orders:confirm:{order_id}"),
                Button.inline("❌ رد سفارش", f"seller:orders:reject:{order_id}")
            ],
            [
                Button.inline("🚚 ثبت ارسال", f"seller:orders:ship:{order_id}"),
                Button.inline("📝 افزودن توضیحات", f"seller:orders:note:{order_id}")
            ],
            [
                Button.inline("« بازگشت", "seller:orders:back")
            ]
        ]
    
    @staticmethod
    def get_seller_payment_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت پرداخت فروشنده"""
        return [
            [
                Button.inline("💰 موجودی حساب", "seller:payment:balance"),
                Button.inline("💸 برداشت وجه", "seller:payment:withdraw")
            ],
            [
                Button.inline("💳 روش‌های پرداخت", "seller:payment:methods"),
                Button.inline("📊 گزارش مالی", "seller:payment:report")
            ],
            [
                Button.inline("« بازگشت", "seller:back")
            ]
        ]
    
    @staticmethod
    def get_seller_payment_methods(payment_methods: List) -> List[List[Button]]:
        """دکمه‌های روش‌های پرداخت فروشنده با نمایش دکمه‌های مدیریت برای هر روش"""
        buttons = []
        
        for method in payment_methods:
            method_id = method.id
            method_name = method.name
            method_active = method.is_active
            
            # دکمه اصلی روش پرداخت
            active_status = "✅" if method_active else "❌"
            buttons.append([Button.inline(f"{active_status} {method_name}", f"seller:payment:view:{method_id}")])
            
            # دکمه‌های عملیات روش پرداخت
            toggle_text = "غیرفعال‌سازی" if method_active else "فعال‌سازی"
            toggle_action = "deactivate" if method_active else "activate"
            
            buttons.append([
                Button.inline(f"✏️ ویرایش", f"seller:payment:edit:{method_id}"),
                Button.inline(f"🔄 {toggle_text}", f"seller:payment:{toggle_action}:{method_id}")
            ])
        
        # دکمه افزودن روش پرداخت جدید
        buttons.append([Button.inline("➕ افزودن روش پرداخت", "seller:payment:add")])
        buttons.append([Button.inline("« بازگشت", "seller:back")])
        
        return buttons
    
    @staticmethod
    def get_seller_reports_keyboard() -> List[List[Button]]:
        """دکمه‌های گزارشات فروشنده"""
        return [
            [
                Button.inline("📊 گزارش فروش", "seller:reports:sales"),
                Button.inline("📈 نمودار فروش", "seller:reports:charts")
            ],
            [
                Button.inline("💰 گزارش مالی", "seller:reports:financial"),
                Button.inline("📦 گزارش محصولات", "seller:reports:products")
            ],
            [
                Button.inline("🕒 بازه زمانی", "seller:reports:period"),
                Button.inline("« بازگشت", "seller:back")
            ]
        ] 