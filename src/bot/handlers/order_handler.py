from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import (
    User, Order, CartItem, Payment, PaymentStatus, OrderStatus,
    PreLocation, MainLocation, Notification, Product
)
from src.bot.common.messages import Messages
from src.config.settings import get_settings
from decimal import Decimal
from typing import Dict, List, Any
import logging
from src.bot.common.keyboards import OrderKeyboards, PaymentKeyboards, BaseKeyboard
from src.core.exceptions import ValidationError, OrderError
from src.core.services.order_manager import OrderManager
from src.core.services.payment_manager import PaymentManager
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderHandler:
    def __init__(self, client):
        self.client = client
        self.settings = get_settings()
        self.user_states: Dict[int, Dict] = {}
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="next_step"))
        async def start_checkout(event):
            """شروع فرایند تکمیل خرید"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    # دریافت اطلاعات کاربر و سبد خرید
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    cart_items = db.query(CartItem).filter(
                        CartItem.user_id == user.id,
                        CartItem.quantity > 0
                    ).all()

                    if not cart_items:
                        await event.answer("سبد خرید شما خالی است!", alert=True)
                        return

                    # محاسبه مجموع قیمت
                    total_amount = sum(item.quantity * item.product.price for item in cart_items)
                    
                    # نمایش گزینه‌های پرداخت
                    message = (
                        f"💰 مجموع سبد خرید: {total_amount:,} تومان\n"
                        f"💳 موجودی شما: {user.balance:,} تومان\n\n"
                    )

                    buttons = PaymentKeyboard.get_payment_methods(total_amount, user.balance)

                    # ذخیره اطلاعات در state
                    self.user_states[user_id] = {
                        "cart_items": [(item.product_id, item.quantity) for item in cart_items],
                        "total_amount": float(total_amount),
                        "remaining_amount": float(remaining) if remaining > 0 else 0
                    }

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in start_checkout: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="pay_with_balance"))
        async def pay_with_balance(event):
            """پرداخت کامل با موجودی"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                if not state:
                    await event.answer("خطا: لطفاً فرایند خرید را از ابتدا شروع کنید.", alert=True)
                    return

                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    total_amount = Decimal(str(state["total_amount"]))

                    if user.balance < total_amount:
                        await event.answer("موجودی شما کافی نیست!", alert=True)
                        return

                    # ایجاد سفارش‌ها
                    orders = []
                    for product_id, quantity in state["cart_items"]:
                        product = db.query(Product).get(product_id)
                        order = Order(
                            buyer_id=user.id,
                            product_id=product_id,
                            quantity=quantity,
                            unit_price=product.price,
                            total_price=product.price * quantity,
                            status=OrderStatus.PENDING_SELLER_CONFIRMATION
                        )
                        orders.append(order)
                        db.add(order)

                    # کسر از موجودی
                    user.balance -= total_amount
                    
                    # ثبت تراکنش
                    payment = Payment(
                        user_id=user.id,
                        amount=total_amount,
                        status=PaymentStatus.CONFIRMED,
                        payment_type='ORDER',
                        transaction_id=f"BALANCE_{user_id}_{orders[0].id}"
                    )
                    db.add(payment)

                    # خالی کردن سبد خرید
                    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
                    
                    # ارسال نوتیفیکیشن به خریدار
                    buyer_notif = Notification(
                        user_id=user.id,
                        title="✅ سفارش با موفقیت ثبت شد",
                        message=f"سفارش شما به مبلغ {total_amount:,} تومان با موفقیت ثبت شد."
                    )
                    db.add(buyer_notif)

                    # ارسال نوتیفیکیشن به فروشندگان
                    for order in orders:
                        seller_notif = Notification(
                            user_id=order.product.seller_id,
                            title="🛍 سفارش جدید",
                            message=f"سفارش جدید برای محصول {order.product.name}"
                        )
                        db.add(seller_notif)
                        
                        # ارسال پیام به فروشنده
                        await self.client.send_message(
                            order.product.seller.telegram_id,
                            f"🛍 سفارش جدید:\n\n"
                            f"محصول: {order.product.name}\n"
                            f"تعداد: {order.quantity}\n"
                            f"مبلغ کل: {order.total_price:,} تومان",
                            buttons=OrderKeyboards.get_order_details_buttons(order.id)
                        )

                    db.commit()

                    # حذف state
                    del self.user_states[user_id]

                    await event.edit(
                        "✅ سفارش شما با موفقیت ثبت شد\n"
                        "لطفاً منتظر تایید فروشنده بمانید.",
                        buttons=[[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]
                    )

            except Exception as e:
                logger.error(f"Error in pay_with_balance: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="pay_crypto"))
        async def handle_crypto_payment(event):
            try:
                buttons = PaymentKeyboard.get_crypto_options()
                await event.edit(Messages.SELECT_CRYPTO, buttons=buttons)
            except Exception as e:
                logger.error(f"Error in handle_crypto_payment: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        # ... سایر هندلرها ...

    async def handle_order_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle order commands"""
        try:
            command = message.get('text', '').split()[0].lower()
            
            if command == '/orders':
                await self.handle_list_orders(message, context)
            elif command == '/order':
                await self.handle_order_details(message, context)
            elif command == '/cancel_order':
                await self.handle_cancel_order(message, context)
            elif command == '/order_status':
                await self.handle_order_status(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid order command. Available commands:\n"
                         "/orders - List your orders\n"
                         "/order <id> - View order details\n"
                         "/cancel_order <id> - Cancel an order\n"
                         "/order_status <id> - Check order status"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing order command: {str(e)}"
            )

    async def handle_list_orders(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /orders command"""
        try:
            user_id = message['from']['id']
            orders = self.order_manager.get_user_orders(user_id)
            
            if not orders:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="You haven't placed any orders yet."
                )
                return
            
            orders_text = "📋 Your Orders:\n\n"
            for order in orders:
                orders_text += (
                    f"Order #{order.id}\n"
                    f"Amount: {order.total_amount} USDT\n"
                    f"Status: {order.status}\n"
                    f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            
            orders_text += "Use /order <id> to view more details about a specific order."
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=orders_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error listing orders: {str(e)}"
            )

    async def handle_order_details(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /order command"""
        try:
            # Get order ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the order ID")
            
            order_id = int(parts[1])
            user_id = message['from']['id']
            
            # Get order details
            order = self.order_manager.get_order(order_id)
            if not order:
                raise OrderError("Order not found")
            
            if order.user_id != user_id:
                raise OrderError("You don't have permission to view this order")
            
            # Get order items
            items = self.order_manager.get_order_items(order_id)
            
            details_text = (
                f"📦 Order Details:\n\n"
                f"Order ID: #{order.id}\n"
                f"Status: {order.status}\n"
                f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Amount: {order.total_amount} USDT\n\n"
                "Items:\n"
            )
            
            for item in items:
                details_text += (
                    f"• {item.product.name}\n"
                    f"  Quantity: {item.quantity}\n"
                    f"  Price: {item.price} USDT\n"
                    f"  Subtotal: {item.quantity * item.price} USDT\n\n"
                )
            
            if order.status == 'pending':
                details_text += "Use /cancel_order to cancel this order."
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=details_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing order details: {str(e)}"
            )

    async def handle_cancel_order(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /cancel_order command"""
        try:
            # Get order ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the order ID")
            
            order_id = int(parts[1])
            user_id = message['from']['id']
            
            # Cancel order
            order = self.order_manager.cancel_order(order_id, user_id)
            
            cancel_text = (
                "✅ Order Cancelled!\n\n"
                f"Order ID: #{order.id}\n"
                f"Status: {order.status}\n"
                f"Cancelled at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "Use /orders to view your orders."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=cancel_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error cancelling order: {str(e)}"
            )

    async def handle_order_status(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /order_status command"""
        try:
            # Get order ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the order ID")
            
            order_id = int(parts[1])
            user_id = message['from']['id']
            
            # Get order status
            order = self.order_manager.get_order(order_id)
            if not order:
                raise OrderError("Order not found")
            
            if order.user_id != user_id:
                raise OrderError("You don't have permission to view this order")
            
            # Get payment status if order is paid
            payment_status = None
            if order.status == 'paid':
                payment = self.payment_manager.get_order_payment(order_id)
                if payment:
                    payment_status = payment.status
            
            status_text = (
                "📊 Order Status:\n\n"
                f"Order ID: #{order.id}\n"
                f"Status: {order.status}\n"
                f"Created: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Amount: {order.total_amount} USDT\n"
            )
            
            if payment_status:
                status_text += f"Payment Status: {payment_status}\n"
            
            if order.status == 'pending':
                status_text += "\nUse /cancel_order to cancel this order."
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=status_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error checking order status: {str(e)}"
            )
