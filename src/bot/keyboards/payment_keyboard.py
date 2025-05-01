from telethon import Button
from typing import List, Any, Union
from src.bot.keyboards.shared_keyboard import BaseKeyboard, KeyboardTexts

class PaymentKeyboards:
    @staticmethod
    def get_crypto_payment_options() -> List[List[Button]]:
        """دکمه‌های پرداخت با ارز دیجیتال"""
        return [
            [
                Button.inline(KeyboardTexts.PAYMENT_BTC, "pay_crypto_btc"),
                Button.inline(KeyboardTexts.PAYMENT_ETH, "pay_crypto_eth")
            ],
            [
                Button.inline(KeyboardTexts.PAYMENT_USDT, "pay_crypto_usdt"),
                Button.inline(KeyboardTexts.PAYMENT_BNB, "pay_crypto_bnb")
            ],
            [
                Button.inline(KeyboardTexts.PAYMENT_VERIFY, "verify_crypto_payment"),
                Button.inline(KeyboardTexts.CANCEL, "cancel_payment")
            ]
        ]

    @staticmethod
    def get_payment_verification() -> List[List[Button]]:
        """دکمه‌های تأیید پرداخت"""
        return [
            [Button.inline(KeyboardTexts.PAYMENT_VERIFY, "verify_payment")],
            [Button.inline(KeyboardTexts.RETRY, "retry_payment")],
            [Button.inline(KeyboardTexts.CANCEL, "cancel_payment")]
        ]
        
    @staticmethod
    def get_add_funds_keyboard() -> List[List[Button]]:
        """
        Get the keyboard for adding funds
        
        Returns:
            List of button rows
        """
        return [
            [
                Button.inline("💳 کارت به کارت", "payment:add_funds:card"),
                Button.inline("💰 ارز دیجیتال", "payment:add_funds:crypto")
            ],
            [
                Button.inline("« بازگشت", "wallet:back")
            ]
        ]
    
    @staticmethod
    def get_payment_methods(total_amount: float, user_balance: float) -> List[List[Button]]:
        """دکمه‌های روش‌های پرداخت"""
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

class CardholderPaymentKeyboards:
    @staticmethod
    def get_cardholder_payment_keyboard(payments: List[Any]) -> List[List[Button]]:
        """
        Get the keyboard for cardholder payment verification
        
        Args:
            payments: List of pending payments
            
        Returns:
            List of button rows
        """
        keyboard = []
        
        # Add buttons for each payment
        for payment in payments:
            payment_id = payment.id
            keyboard.append([
                Button.inline(f"✅ تأیید #{payment_id}", f"payment:approve:{payment_id}"),
                Button.inline(f"❌ رد #{payment_id}", f"payment:reject:{payment_id}")
            ])
        
        # Add navigation buttons
        keyboard.append([
            Button.inline("« بازگشت", "navigation:main_menu"),
            Button.inline("🔄 بروزرسانی", "payment:refresh")
        ])
        
        return keyboard

class AdminPaymentKeyboards:
    @staticmethod
    def get_admin_payment_keyboard(payments: List[Any]) -> List[List[Button]]:
        """
        Get the keyboard for admin payment verification
        
        Args:
            payments: List of pending payments
            
        Returns:
            List of button rows
        """
        keyboard = []
        
        # Add buttons for each payment
        for payment in payments:
            payment_id = payment.id
            keyboard.append([
                Button.inline(f"✅ تأیید #{payment_id}", f"admin:payment:confirm:{payment_id}"),
                Button.inline(f"❌ رد #{payment_id}", f"admin:payment:reject:{payment_id}")
            ])
        
        # Add navigation buttons
        keyboard.append([
            Button.inline("« بازگشت", "navigation:admin_menu"),
            Button.inline("🔄 بروزرسانی", "admin:payment:refresh")
        ])
        
        return keyboard

    @staticmethod
    def get_admin_payments_keyboard() -> List[List[Button]]:
        """
        Get the keyboard for admin payments management
        
        Returns:
            List of button rows
        """
        return [
            [
                Button.inline("🕒 پرداخت‌های در انتظار", "admin:payment:pending"),
                Button.inline("✅ پرداخت‌های تکمیل شده", "admin:payment:completed")
            ],
            [
                Button.inline("📊 گزارش مالی", "admin:payment:export"),
                Button.inline("⚙️ تنظیمات پرداخت", "admin:payment:settings")
            ],
            [
                Button.inline("« بازگشت", "admin:back")
            ]
        ]

class BalanceKeyboards:
    @staticmethod
    def get_charge_options() -> List[List[Button]]:
        """دکمه‌های گزینه‌های شارژ کیف پول"""
        return [
            [Button.inline("💳 شارژ با کارت بانکی", "charge_card")],
            [Button.inline("💎 شارژ با ارز دیجیتال", "charge_crypto")],
            [Button.inline("🧾 مشاهده تراکنش‌های قبلی", "view_transactions")],
            [Button.inline("❓ راهنمای شارژ", "charge_help")],
            [Button.inline("🔙 بازگشت", "back_to_wallet")]
        ]

    @staticmethod 
    def get_charge_amounts() -> List[List[Button]]:
        """دکمه‌های مبالغ پیش‌فرض شارژ"""
        return [
            [
                Button.inline("💰 ۵۰,۰۰۰ تومان", "charge_amount_50000"),
                Button.inline("💰 ۱۰۰,۰۰۰ تومان", "charge_amount_100000")
            ],
            [
                Button.inline("💰 ۲۰۰,۰۰۰ تومان", "charge_amount_200000"),
                Button.inline("💰 ۵۰۰,۰۰۰ تومان", "charge_amount_500000")
            ],
            [
                Button.inline("💰 ۱,۰۰۰,۰۰۰ تومان", "charge_amount_1000000"),
                Button.inline("✏️ مبلغ دلخواه", "charge_amount_custom")
            ],
            [
                Button.inline("🔙 بازگشت", "back_to_charge_options")
            ]
        ]

class SupportKeyboards:
    @staticmethod
    def get_support_options() -> List[List[Button]]:
        """دکمه‌های گزینه‌های پشتیبانی"""
        return [
            [
                Button.inline(KeyboardTexts.SUPPORT_FAQ, "faq"),
                Button.inline(KeyboardTexts.SUPPORT_NEW_TICKET, "new_ticket")
            ],
            [
                Button.inline(KeyboardTexts.SUPPORT_MY_TICKETS, "my_tickets")
            ],
            [
                Button.inline(KeyboardTexts.BACK_TO_MAIN, "back_to_main")
            ]
        ]

    @staticmethod
    def get_ticket_actions(ticket_id: int) -> List[List[Button]]:
        """دکمه‌های عملیات درخواست پشتیبانی"""
        return [
            [
                Button.inline(KeyboardTexts.SUPPORT_REPLY, f"reply_ticket_{ticket_id}"),
                Button.inline(KeyboardTexts.SUPPORT_CLOSE, f"close_ticket_{ticket_id}")
            ],
            [
                Button.inline(KeyboardTexts.BACK, "back_to_tickets")
            ]
        ] 