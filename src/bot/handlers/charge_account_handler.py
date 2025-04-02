import decimal
from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, PaymentMethod, BankCard, Payment, PaymentStatus
from src.bot.common.messages import Messages
from src.config.settings import get_settings
from decimal import Decimal
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ChargeAccountHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.settings = get_settings()
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="💳 Charge Account"))
        async def show_balance(event):
            """نمایش موجودی فعلی و گزینه‌های شارژ حساب"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return
                    
                    message = (
                        f"💰 موجودی فعلی شما: {user.balance:,.0f} تومان\n\n"
                        "برای افزایش موجودی یکی از روش‌های زیر را انتخاب کنید:"
                    )
                    
                    buttons = [
                        [Button.inline("💳 پرداخت با کارت", "card_payment")],
                        [Button.inline("💎 پرداخت با ارز دیجیتال", "crypto_payment")],
                        [Button.inline("🔙 بازگشت به منوی اصلی", "back_to_main")]
                    ]
                    
                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in show_balance: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="card_payment"))
        async def start_card_payment(event):
            """شروع فرایند پرداخت با کارت بانکی"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id, {})
                
                # اگر مبلغ از قبل تعیین شده (مثلاً در سبد خرید)
                amount = state.get('required_amount')
                
                if amount:
                    await self.show_bank_cards(event, amount)
                else:
                    self.user_states[user_id] = {
                        "action": "card_payment",
                        "step": "enter_amount"
                    }
                    await event.edit(
                        "💳 لطفاً مبلغ مورد نظر را به تومان وارد کنید:",
                        buttons=[[Button.inline("🔙 انصراف", "cancel_payment")]]
                    )

            except Exception as e:
                logger.error(f"Error in start_card_payment: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_payment_input(event):
            """پردازش ورودی‌های کاربر در فرایند پرداخت"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state:
                return

            try:
                if state["action"] == "card_payment" and state["step"] == "enter_amount":
                    try:
                        # حذف کاراکترهای اضافی و تبدیل اعداد فارسی به انگلیسی
                        amount_text = event.text.strip().replace(",", "")
                        amount_text = amount_text.replace("٠", "0").replace("١", "1").replace("٢", "2")\
                                                .replace("٣", "3").replace("٤", "4").replace("٥", "5")\
                                                .replace("٦", "6").replace("٧", "7").replace("٨", "8")\
                                                .replace("٩", "9")
                        
                        amount = Decimal(amount_text)
                        if amount <= 0:
                            await event.respond("❌ مبلغ وارد شده نامعتبر است!")
                            return
                        
                        await self.show_bank_cards(event, amount)
                        
                    except (ValueError, decimal.InvalidOperation):
                        await event.respond("❌ لطفاً یک عدد معتبر وارد کنید!")
                        return

                elif state["action"] == "card_payment" and state["step"] == "upload_receipt":
                    if event.media:
                        # Get admin user and current user
                        with SessionLocal() as db:
                            admin = db.query(User).filter(
                                User.telegram_id == str(self.settings.HEAD_ADMIN_ID)
                            ).first()
                            
                            current_user = db.query(User).filter(
                                User.telegram_id == str(user_id)
                            ).first()
                            
                            if not admin or not current_user:
                                await event.respond("❌ خطا در ارسال رسید به ادمین!")
                                return
                            
                            amount = state["amount"]
                            payment = Payment(
                                user_id=current_user.id,  # استفاده از current_user به جای user
                                amount=amount,
                                status=PaymentStatus.PENDING,
                                payment_type='CHARGE',
                                transaction_id=f"MANUAL_{user_id}_{event.id}"
                            )
                            db.add(payment)
                            db.commit()
                            
                            # Forward receipt to admin with approve/reject buttons
                            admin_message = (
                                f"🧾 درخواست شارژ حساب:\n\n"
                                f"👤 کاربر: {event.sender.username or event.sender.id}\n"
                                f"💰 مبلغ: {amount:,} تومان\n"
                                f"🆔 شناسه تراکنش: {payment.transaction_id}"
                            )
                            
                            buttons = [
                                [
                                    Button.inline("✅ تایید", f"approve_payment_{payment.id}"),
                                    Button.inline("❌ رد", f"reject_payment_{payment.id}")
                                ]
                            ]
                            
                            # Send to admin
                            await self.client.send_file(
                                admin.telegram_id,
                                file=event.media,
                                caption=admin_message,
                                buttons=buttons
                            )
                            
                            # Notify user
                            await event.respond(
                                "✅ رسید پرداخت شما با موفقیت ارسال شد.\n"
                                "لطفاً منتظر تایید ادمین بمانید."
                            )
                            
                            # Clear user state
                            del self.user_states[user_id]
                    else:
                        await event.respond("❌ لطفاً تصویر فیش واریزی را ارسال کنید!")

            except Exception as e:
                logger.error(f"Error in handle_payment_input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

        @self.client.on(events.CallbackQuery(pattern=r"approve_payment_\d+"))
        async def approve_payment(event):
            """تایید پرداخت توسط ادمین"""
            try:
                if str(event.sender_id) != str(self.settings.HEAD_ADMIN_ID):
                    await event.answer("⛔️ شما دسترسی به این عملیات را ندارید!", alert=True)
                    return
                
                payment_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    payment = db.query(Payment).get(payment_id)
                    if not payment or payment.status != PaymentStatus.PENDING:
                        await event.answer("❌ تراکنش نامعتبر یا قبلاً پردازش شده!", alert=True)
                        return
                    
                    # Get user from transaction ID
                    user_id = payment.transaction_id.split('_')[1]
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    
                    if user:
                        # Update user balance
                        user.balance += payment.amount
                        payment.status = PaymentStatus.CONFIRMED
                        db.commit()
                        
                        # Notify user
                        await self.client.send_message(
                            int(user_id),
                            f"✅ پرداخت شما تایید شد!\n💰 موجودی جدید: {user.balance:,} تومان"
                        )
                        
                        # Get original message
                        original_msg = await event.get_message()
                        if original_msg:
                            # Update admin message
                            await original_msg.edit(
                                original_msg.text + "\n\n✅ تایید شده",
                                buttons=None
                            )
                        
                        await event.answer("✅ پرداخت با موفقیت تایید شد", alert=True)
                    
            except Exception as e:
                logger.error(f"Error in approve_payment: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"reject_payment_\d+"))
        async def reject_payment(event):
            """رد پرداخت توسط ادمین"""
            try:
                if str(event.sender_id) != str(self.settings.HEAD_ADMIN_ID):
                    await event.answer("⛔️ شما دسترسی به این عملیات را ندارید!", alert=True)
                    return
                
                payment_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    payment = db.query(Payment).get(payment_id)
                    if not payment or payment.status != PaymentStatus.PENDING:
                        await event.answer("❌ تراکنش نامعتبر یا قبلاً پردازش شده!", alert=True)
                        return
                    
                    # Get user from transaction ID
                    user_id = payment.transaction_id.split('_')[1]
                    payment.status = PaymentStatus.FAILED
                    db.commit()
                    
                    # Notify user
                    await self.client.send_message(
                        int(user_id),
                        "❌ متأسفانه پرداخت شما تایید نشد.\nلطفاً مجدداً تلاش کنید."
                    )
                    
                    # Update admin message
                    await event.edit(
                        event.message.text + "\n\n❌ رد شده",
                        buttons=None
                    )
                    
            except Exception as e:
                logger.error(f"Error in reject_payment: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def show_bank_cards(self, event, amount: Decimal):
        """نمایش لیست کارت‌های بانکی برای پرداخت"""
        try:
            user_id = event.sender_id
            
            with SessionLocal() as db:
                # Get card payment method
                card_method = db.query(PaymentMethod).filter(
                    PaymentMethod.type == 'CARD',
                    PaymentMethod.is_active == True
                ).first()
                
                if not card_method:
                    await event.respond("❌ در حال حاضر امکان پرداخت با کارت وجود ندارد!")
                    return
                
                # Get active bank cards
                cards = db.query(BankCard).filter(
                    BankCard.payment_method_id == card_method.id
                ).all()
                
                if not cards:
                    await event.respond("❌ هیچ کارت بانکی فعالی یافت نشد!")
                    return
                
                message = (
                    f"💳 لطفاً مبلغ {amount:,} تومان را به یکی از کارت‌های زیر واریز کنید:\n\n"
                )
                
                for card in cards:
                    message += (
                        f"🏦 {card.bank_name}\n"
                        f"👤 {card.card_holder}\n"
                        f"💳 {card.card_number}\n"
                        f"{'─' * 20}\n"
                    )
                
                message += "\n⚠️ پس از واریز، لطفاً تصویر فیش واریزی را ارسال کنید."
                
                # Update user state
                self.user_states[user_id] = {
                    "action": "card_payment",
                    "step": "upload_receipt",
                    "amount": amount
                }
                
                buttons = [[Button.inline("🔙 انصراف", "cancel_payment")]]
                
                # به جای edit از respond استفاده می‌کنیم
                await event.respond(message, buttons=buttons)
                # حذف پیام قبلی
                try:
                    await event.delete()
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Error in show_bank_cards: {e}")
            await event.respond(Messages.ERROR_OCCURRED)
