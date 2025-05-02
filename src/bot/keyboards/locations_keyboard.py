from telethon import Button
from typing import List, Union, Optional, Dict, Any
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

class LocationKeyboards(BaseKeyboard):
    """کلاس مدیریت کیبوردهای مکان‌ها و آدرس‌ها"""
    
    @staticmethod
    def get_province_selection(provinces: List) -> List[List[Button]]:
        """دکمه‌های انتخاب استان"""
        buttons = []
        
        # دو دکمه در هر ردیف
        for i in range(0, len(provinces), 2):
            row = []
            row.append(Button.inline(
                f"🏙️ {provinces[i].name}", 
                f"province:{provinces[i].id}"
            ))
            if i + 1 < len(provinces):
                row.append(Button.inline(
                    f"🏙️ {provinces[i+1].name}", 
                    f"province:{provinces[i+1].id}"
                ))
            buttons.append(row)
        
        # اگر تعداد استان‌ها زیاد است، دکمه‌های صفحه‌بندی اضافه شود
        if len(provinces) > 10:
            buttons.append([
                Button.inline("صفحه بعد »", "provinces:next"),
                Button.inline("« صفحه قبل", "provinces:prev")
            ])
        
        return buttons
    
    @staticmethod
    def get_city_selection(cities: List, province_id: str) -> List[List[Button]]:
        """دکمه‌های انتخاب شهر برای یک استان خاص"""
        buttons = []
        
        # دو دکمه در هر ردیف
        for i in range(0, len(cities), 2):
            row = []
            row.append(Button.inline(
                f"🏙️ {cities[i].name}", 
                f"city:{cities[i].id}"
            ))
            if i + 1 < len(cities):
                row.append(Button.inline(
                    f"🏙️ {cities[i+1].name}", 
                    f"city:{cities[i+1].id}"
                ))
            buttons.append(row)
        
        # اگر تعداد شهرها زیاد است، دکمه‌های صفحه‌بندی اضافه شود
        if len(cities) > 10:
            buttons.append([
                Button.inline("صفحه بعد »", f"cities:next:{province_id}"),
                Button.inline("« صفحه قبل", f"cities:prev:{province_id}")
            ])
        
        # دکمه بازگشت به لیست استان‌ها
        buttons.append([Button.inline("« بازگشت به استان‌ها", "back_to_provinces")])
        
        return buttons
    
    @staticmethod
    def get_location_management() -> List[List[Button]]:
        """دکمه‌های مدیریت مکان کاربر"""
        return [
            [
                Button.inline("🏙️ تغییر استان/شهر", "change_location"),
                Button.inline("📍 نشانی‌های من", "my_addresses")
            ],
            [
                Button.inline("➕ افزودن نشانی جدید", "add_new_address"),
                Button.inline("🔍 مشاهده نشانی فعلی", "view_current_address")
            ],
            [
                Button.inline("« بازگشت به منوی اصلی", "back_to_main")
            ]
        ]
    
    @staticmethod
    def get_address_list(addresses: List) -> List[List[Button]]:
        """دکمه‌های لیست آدرس‌های کاربر"""
        buttons = []
        
        for address in addresses:
            address_id = address.id
            address_title = address.title or f"آدرس {address_id}"
            
            # دکمه هر آدرس
            buttons.append([Button.inline(f"📍 {address_title}", f"address:view:{address_id}")])
            
            # دکمه‌های عملیات برای هر آدرس
            buttons.append([
                Button.inline("✏️ ویرایش", f"address:edit:{address_id}"),
                Button.inline("❌ حذف", f"address:delete:{address_id}"),
                Button.inline("✅ انتخاب", f"address:select:{address_id}")
            ])
        
        # دکمه افزودن آدرس جدید
        buttons.append([Button.inline("➕ افزودن آدرس جدید", "address:add")])
        buttons.append([Button.inline("« بازگشت", "back_to_location")])
        
        return buttons
    
    @staticmethod
    def get_admin_locations_keyboard() -> List[List[Button]]:
        """دکمه‌های مدیریت مکان‌ها برای ادمین"""
        return [
            [
                Button.inline("🏙️ مدیریت استان‌ها", "admin:locations:provinces"),
                Button.inline("🏘️ مدیریت شهرها", "admin:locations:cities")
            ],
            [
                Button.inline("📍 مناطق تحویل", "admin:locations:delivery_areas"),
                Button.inline("🚚 هزینه ارسال", "admin:locations:shipping_costs")
            ],
            [
                Button.inline("« بازگشت", "admin:back")
            ]
        ]
    
    @staticmethod
    def get_admin_province_list(provinces: List) -> List[List[Button]]:
        """دکمه‌های لیست استان‌ها برای ادمین"""
        buttons = []
        
        for province in provinces:
            province_id = province.id
            province_name = province.name
            
            # دکمه هر استان
            buttons.append([Button.inline(f"🏙️ {province_name}", f"admin:locations:province:{province_id}")])
            
            # دکمه‌های عملیات برای هر استان
            buttons.append([
                Button.inline("✏️ ویرایش", f"admin:locations:province:edit:{province_id}"),
                Button.inline("❌ حذف", f"admin:locations:province:delete:{province_id}"),
                Button.inline("🏘️ شهرها", f"admin:locations:province:cities:{province_id}")
            ])
        
        # دکمه افزودن استان جدید
        buttons.append([Button.inline("➕ افزودن استان", "admin:locations:province:add")])
        buttons.append([Button.inline("« بازگشت", "admin:locations:back")])
        
        return buttons
    
    @staticmethod
    def get_admin_city_list(cities: List, province_id: Optional[str] = None) -> List[List[Button]]:
        """دکمه‌های لیست شهرها برای ادمین"""
        buttons = []
        
        for city in cities:
            city_id = city.id
            city_name = city.name
            
            # دکمه هر شهر
            buttons.append([Button.inline(f"🏘️ {city_name}", f"admin:locations:city:{city_id}")])
            
            # دکمه‌های عملیات برای هر شهر
            buttons.append([
                Button.inline("✏️ ویرایش", f"admin:locations:city:edit:{city_id}"),
                Button.inline("❌ حذف", f"admin:locations:city:delete:{city_id}"),
                Button.inline("📍 مناطق", f"admin:locations:city:areas:{city_id}")
            ])
        
        # دکمه افزودن شهر جدید
        if province_id:
            buttons.append([Button.inline("➕ افزودن شهر", f"admin:locations:city:add:{province_id}")])
            buttons.append([Button.inline("« بازگشت به استان", f"admin:locations:province:{province_id}")])
        else:
            buttons.append([Button.inline("➕ افزودن شهر", "admin:locations:city:add")])
            buttons.append([Button.inline("« بازگشت", "admin:locations:back")])
        
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