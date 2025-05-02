from telethon import Button
from typing import List, Union, Optional, Dict, Any
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

class ProductKeyboards(BaseKeyboard):
    """کلاس مدیریت کیبوردهای مرتبط با محصولات"""
    
    @staticmethod
    def get_product_categories() -> List[List[Button]]:
        """دکمه‌های دسته‌بندی‌های محصول"""
        return [
            [
                Button.inline(KeyboardTexts.CATEGORY_DIGITAL, "category_digital"),
                Button.inline(KeyboardTexts.CATEGORY_CLOTHES, "category_clothes")
            ],
            [
                Button.inline(KeyboardTexts.CATEGORY_FOOD, "category_food"),
                Button.inline(KeyboardTexts.CATEGORY_HEALTH, "category_health")
            ],
            [
                Button.inline(KeyboardTexts.CATEGORY_BOOKS, "category_books"),
                Button.inline(KeyboardTexts.CATEGORY_SPORTS, "category_sports")
            ],
            [
                Button.inline(KeyboardTexts.SEARCH_PRODUCTS, "search_products"),
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]
    
    @staticmethod
    def get_product_pagination(current_page: int, total_pages: int, category_id: Optional[str] = None) -> List[List[Button]]:
        """دکمه‌های صفحه‌بندی محصولات"""
        buttons = []
        navigation = []
        
        prefix = f"cat_{category_id}_" if category_id else ""
        
        if current_page > 1:
            navigation.append(Button.inline(KeyboardTexts.PREVIOUS_PAGE, f"{prefix}page_{current_page-1}"))
        
        if current_page < total_pages:
            navigation.append(Button.inline(KeyboardTexts.NEXT_PAGE, f"{prefix}page_{current_page+1}"))
        
        if navigation:
            buttons.append(navigation)
        
        buttons.append([Button.inline(KeyboardTexts.BACK_TO_CATEGORIES, f"{prefix}back_to_categories")])
        buttons.append([Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")])
        
        return buttons
    
    @staticmethod
    def get_product_details(product_id: str, in_stock: bool = True) -> List[List[Button]]:
        """دکمه‌های جزئیات محصول"""
        buttons = []
        
        if in_stock:
            buttons.append([Button.inline(KeyboardTexts.ADD_TO_CART, f"add_to_cart_{product_id}")])
        
        buttons.extend([
            [
                Button.inline(KeyboardTexts.PRODUCT_REVIEWS, f"reviews_{product_id}"),
                Button.inline(KeyboardTexts.PRODUCT_SPECS, f"specs_{product_id}")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_PRODUCTS, "back_to_products"),
                Button.inline(KeyboardTexts.VIEW_CART, "view_cart")
            ]
        ])
        
        return buttons
    
    @staticmethod
    def get_product_search_options() -> List[List[Button]]:
        """دکمه‌های جستجوی محصول"""
        return [
            [
                Button.inline(KeyboardTexts.SEARCH_BY_NAME, "search_by_name"),
                Button.inline(KeyboardTexts.SEARCH_BY_PRICE, "search_by_price")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_CATEGORIES, "back_to_categories")
            ]
        ]
    
    @staticmethod
    def get_product_reviews(product_id: str) -> List[List[Button]]:
        """دکمه‌های نظرات محصول"""
        return [
            [
                Button.inline(KeyboardTexts.ADD_REVIEW, f"add_review_{product_id}"),
                Button.inline(KeyboardTexts.BACK_TO_PRODUCT, f"back_to_product_{product_id}")
            ]
        ]
        
    # مدیریت محصولات برای ادمین
    @staticmethod
    def get_admin_products_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت محصولات برای ادمین"""
        return [
            [
                Button.inline("➕ افزودن محصول", "admin:product:add"),
                Button.inline("🔍 جستجوی محصول", "admin:product:search")
            ],
            [
                Button.inline("📋 لیست محصولات", "admin:product:list"),
                Button.inline("📦 دسته‌بندی‌ها", "admin:product:categories")
            ],
            [
                Button.inline("« بازگشت", "admin:back")
            ]
        ]
        
    @staticmethod
    def get_product_management(product_id: str) -> List[List[Button]]:
        """دکمه‌های مدیریت یک محصول خاص برای ادمین"""
        return [
            [
                Button.inline("✏️ ویرایش محصول", f"admin:product:edit:{product_id}"),
                Button.inline("🖼️ مدیریت تصاویر", f"admin:product:images:{product_id}")
            ],
            [
                Button.inline("🏷️ قیمت و موجودی", f"admin:product:inventory:{product_id}"),
                Button.inline("🗑️ حذف محصول", f"admin:product:delete:{product_id}")
            ],
            [
                Button.inline("« بازگشت به لیست", "admin:product:back_to_list")
            ]
        ]
    
    @staticmethod
    def get_product_options(product_id: str) -> List[List[Button]]:
        """دکمه‌های تنظیمات یک محصول برای ادمین"""
        return [
            [
                Button.inline("✅ فعال", f"admin:product:enable:{product_id}"),
                Button.inline("❌ غیرفعال", f"admin:product:disable:{product_id}")
            ],
            [
                Button.inline("⭐ ویژه کردن", f"admin:product:featured:{product_id}"),
                Button.inline("🏷️ افزودن تگ", f"admin:product:add_tag:{product_id}")
            ],
            [
                Button.inline("« بازگشت", f"admin:product:back:{product_id}")
            ]
        ]
    
    @staticmethod
    def get_product_details_keyboard(product_id: str) -> List[List[Button]]:
        """دکمه‌های جزئیات محصول برای ادمین"""
        return [
            [
                Button.inline("📊 آمار فروش", f"admin:product:stats:{product_id}"),
                Button.inline("💬 نظرات کاربران", f"admin:product:reviews:{product_id}")
            ],
            [
                Button.inline("« بازگشت", f"admin:product:back:{product_id}")
            ]
        ]
    
    @staticmethod
    def get_product_list_keyboard(page: int = 1, total_pages: int = 1) -> List[List[Button]]:
        """دکمه‌های لیست محصولات برای ادمین"""
        buttons = []
        
        # دکمه‌های صفحه‌بندی
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:product:list:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:product:list:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # دکمه‌های فیلتر
        buttons.append([
            Button.inline("🔍 فیلتر", "admin:product:filter"),
            Button.inline("🔄 بروزرسانی", f"admin:product:refresh:{page}")
        ])
        
        # دکمه بازگشت
        buttons.append([
            Button.inline("« بازگشت", "admin:product:back_to_menu")
        ])
        
        return buttons

class CategoryKeyboards:
    @staticmethod
    def get_categories_list(categories: List) -> List[List[Button]]:
        """دکمه‌های لیست دسته‌بندی‌ها"""
        buttons = []
        # دو دکمه در هر ردیف
        for i in range(0, len(categories), 2):
            row = []
            row.append(Button.inline(
                f"📁 {categories[i].name}", 
                f"category_{categories[i].id}"
            ))
            if i + 1 < len(categories):
                row.append(Button.inline(
                    f"📁 {categories[i+1].name}", 
                    f"category_{categories[i+1].id}"
                ))
            buttons.append(row)
        
        buttons.append([Button.inline("➕ افزودن دسته‌بندی", "add_category")])
        buttons.append([Button.inline("🔙 بازگشت", "back_to_admin")])
        return buttons

    @staticmethod
    def get_category_options(category_id: int) -> List[List[Button]]:
        """دکمه‌های عملیات دسته‌بندی"""
        return [
            [Button.inline("✏️ ویرایش", f"edit_category_{category_id}")],
            [Button.inline("❌ حذف", f"delete_category_{category_id}")],
            [Button.inline("📦 مشاهده محصولات", f"view_category_products_{category_id}")],
            [Button.inline("🔙 بازگشت به دسته‌بندی‌ها", "back_to_categories")]
        ]
        
    @staticmethod
    def get_admin_category_list(categories: List) -> List[List[Button]]:
        """دکمه‌های مدیریت دسته‌بندی‌ها برای ادمین با نمایش دکمه‌های ویرایش و حذف برای هر دسته‌بندی"""
        buttons = []
        
        for category in categories:
            cat_id = category.id
            cat_name = category.name
            
            # دکمه‌های عملیات برای هر دسته‌بندی
            buttons.append([Button.inline(f"📁 {cat_name}", f"admin:category:view:{cat_id}")])
            buttons.append([
                Button.inline("✏️ ویرایش", f"admin:category:edit:{cat_id}"),
                Button.inline("❌ حذف", f"admin:category:delete:{cat_id}")
            ])
        
        # دکمه افزودن دسته‌بندی جدید
        buttons.append([Button.inline("➕ افزودن دسته‌بندی", "admin:category:add")])
        buttons.append([Button.inline("« بازگشت", "admin:products:back")])
        
        return buttons
    
    @staticmethod
    def get_seller_category_request() -> List[List[Button]]:
        """دکمه‌های درخواست افزودن دسته‌بندی برای فروشنده"""
        return [
            [Button.inline("➕ درخواست دسته‌بندی جدید", "seller:category:request")],
            [Button.inline("📋 درخواست‌های قبلی", "seller:category:requests")],
            [Button.inline("« بازگشت", "seller:back")]
        ] 