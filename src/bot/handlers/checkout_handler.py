from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import (
    User, Order, CartItem, Payment, PaymentStatus, OrderStatus,
    PreLocation, MainLocation, Notification, Product
)
from src.bot.common.messages import Messages
from src.config.settings import get_settings
from decimal import Decimal
from typing import Dict, List
import logging
from src.bot.common.keyboards import OrderKeyboards, PaymentKeyboards, BaseKeyboard

logger = logging.getLogger(__name__)

class CheckoutHandler:
    def __init__(self, client):
        self.client = client
        self.settings = get_settings()
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="start_checkout"))
        async def handle_checkout_start(event):
            """شروع فرایند تکمیل خرید"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                    # بررسی سبد خرید
                    cart_items = db.query(CartItem).filter(
                        CartItem.user_id == user.id,
                        CartItem.quantity > 0
                    ).all()

                    if not cart_items:
                        await event.answer("سبد خرید شما خالی است!", alert=True)
                        return

                    # محاسبه مجموع قیمت
                    total_amount = sum(item.quantity * item.product.price for item in cart_items)

                    # ذخیره اطلاعات در state
                    self.user_states[user_id] = {
                        "step": "address",
                        "cart_items": [(item.product_id, item.quantity) for item in cart_items],
                        "total_amount": float(total_amount)
                    }

                    # نمایش فرم آدرس
                    message = (
                        "🏠 لطفاً آدرس دقیق خود را وارد کنید:\n\n"
                        "نکته: آدرس باید شامل استان، شهر، خیابان و پلاک باشد."
                    )
                    buttons = [[Button.inline("🔙 بازگشت", "back_to_cart")]]
                    
                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_checkout_start: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_checkout_input(event):
            """پردازش ورودی‌های کاربر در فرایند خرید"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or "step" not in state:
                    return

                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    if not user:
                        return

                    if state["step"] == "address":
                        # ذخیره آدرس و نمایش تایید
                        address = event.text.strip()
                        if len(address) < 10:
                            await event.respond(
                                "❌ آدرس وارد شده خیلی کوتاه است. لطفاً آدرس کامل را وارد کنید.",
                                buttons=[[Button.inline("🔙 بازگشت", "back_to_cart")]]
                            )
                            return

                        state["address"] = address
                        state["step"] = "confirm"

                        # نمایش خلاصه سفارش
                        cart_items = []
                        total_amount = Decimal('0')
                        
                        for product_id, quantity in state["cart_items"]:
                            product = db.query(Product).get(product_id)
                            if product:
                                item_total = product.price * quantity
                                total_amount += item_total
                                cart_items.append(
                                    f"📦 {product.name}\n"
                                    f"تعداد: {quantity}\n"
                                    f"قیمت واحد: {int(product.price):,} تومان\n"
                                    f"جمع: {int(item_total):,} تومان\n"
                                    f"{'─' * 20}"
                                )

                        message = (
                            "📋 خلاصه سفارش:\n\n"
                            f"{''.join(cart_items)}\n"
                            f"💰 مجموع کل: {int(total_amount):,} تومان\n\n"
                            f"🏠 آدرس ارسال:\n{address}\n\n"
                            "لطفاً سفارش خود را تایید کنید."
                        )

                        buttons = [
                            [Button.inline("✅ تایید و پرداخت", "confirm_order")],
                            [Button.inline("✏️ ویرایش آدرس", "edit_address")],
                            [Button.inline("🔙 بازگشت به سبد خرید", "back_to_cart")]
                        ]

                        await event.respond(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_checkout_input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

        @self.client.on(events.CallbackQuery(pattern="confirm_order"))
        async def handle_order_confirmation(event):
            """تایید نهایی سفارش و انتقال به بخش پرداخت"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or "step" not in state or state["step"] != "confirm":
                    await event.answer("خطا: لطفاً فرایند خرید را از ابتدا شروع کنید.", alert=True)
                    return

                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    total_amount = Decimal(str(state["total_amount"]))

                    # نمایش گزینه‌های پرداخت
                    message = (
                        f"💰 مبلغ قابل پرداخت: {int(total_amount):,} تومان\n"
                        f"💳 موجودی کیف پول: {int(user.balance):,} تومان\n\n"
                        "لطفاً روش پرداخت را انتخاب کنید:"
                    )

                    buttons = [
                        [Button.inline("💰 پرداخت با موجودی", "pay_with_balance")] if user.balance >= total_amount else None,
                        [Button.inline("💳 پرداخت آنلاین", "pay_online")],
                        [Button.inline("🔙 بازگشت", "back_to_confirm")]
                    ]
                    buttons = [b for b in buttons if b is not None]

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_order_confirmation: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="edit_address"))
        async def handle_address_edit(event):
            """ویرایش آدرس"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state:
                    await event.answer("خطا: لطفاً فرایند خرید را از ابتدا شروع کنید.", alert=True)
                    return

                state["step"] = "address"
                message = (
                    "🏠 لطفاً آدرس جدید خود را وارد کنید:\n\n"
                    "نکته: آدرس باید شامل استان، شهر، خیابان و پلاک باشد."
                )
                buttons = [[Button.inline("🔙 بازگشت", "back_to_cart")]]
                
                await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_address_edit: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_confirm"))
        async def handle_back_to_confirm(event):
            """بازگشت به مرحله تایید سفارش"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or "address" not in state:
                    await event.answer("خطا: لطفاً فرایند خرید را از ابتدا شروع کنید.", alert=True)
                    return

                with SessionLocal() as db:
                    cart_items = []
                    total_amount = Decimal('0')
                    
                    for product_id, quantity in state["cart_items"]:
                        product = db.query(Product).get(product_id)
                        if product:
                            item_total = product.price * quantity
                            total_amount += item_total
                            cart_items.append(
                                f"📦 {product.name}\n"
                                f"تعداد: {quantity}\n"
                                f"قیمت واحد: {int(product.price):,} تومان\n"
                                f"جمع: {int(item_total):,} تومان\n"
                                f"{'─' * 20}"
                            )

                    message = (
                        "📋 خلاصه سفارش:\n\n"
                        f"{''.join(cart_items)}\n"
                        f"💰 مجموع کل: {int(total_amount):,} تومان\n\n"
                        f"🏠 آدرس ارسال:\n{state['address']}\n\n"
                        "لطفاً سفارش خود را تایید کنید."
                    )

                    buttons = [
                        [Button.inline("✅ تایید و پرداخت", "confirm_order")],
                        [Button.inline("✏️ ویرایش آدرس", "edit_address")],
                        [Button.inline("🔙 بازگشت به سبد خرید", "back_to_cart")]
                    ]

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_back_to_confirm: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_cart"))
        async def handle_back_to_cart(event):
            """بازگشت به سبد خرید"""
            try:
                user_id = event.sender_id
                if user_id in self.user_states:
                    del self.user_states[user_id]
                
                # بازگشت به صفحه سبد خرید
                await event.edit("در حال بازگشت به سبد خرید...", buttons=None)
                await self.client.emit(events.CallbackQuery.Event(data=b"show_cart"))

            except Exception as e:
                logger.error(f"Error in handle_back_to_cart: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)
