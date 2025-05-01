from telethon import Button
from typing import List, Union
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

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