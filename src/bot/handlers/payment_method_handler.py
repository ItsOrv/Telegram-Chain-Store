from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import PaymentMethod, BankCard, User, UserRole
from src.bot.common.messages import Messages
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class PaymentMethodHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="payment_methods"))  # تغییر pattern
        async def show_payment_methods(event):
            """Show available payment methods"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(
                        User.telegram_id == str(user_id),
                        User.role == UserRole.ADMIN
                    ).first()
                    
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                    methods = db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()
                    
                    message = "💳 متدهای پرداخت موجود:\n\n"
                    buttons = []

                    for method in methods:
                        buttons.append([Button.inline(
                            f"{'💎' if method.type == 'CRYPTO' else '💳' if method.type == 'CARD' else '💵'} {method.name}",
                            f"view_method_{method.id}"
                        )])

                    buttons.extend([
                        [Button.inline("➕ افزودن متد جدید", "add_payment_method")],
                        [Button.inline("🔙 بازگشت به منوی اصلی", "back_to_main")]
                    ])

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in show_payment_methods: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"view_method_\d+"))
        async def view_payment_method(event):
            """Show payment method details"""
            try:
                method_id = int(event.data.decode().split('_')[2])
                with SessionLocal() as db:
                    method = db.query(PaymentMethod).get(method_id)
                    
                    if method.type == 'CARD':
                        # نمایش لیست کارت‌ها
                        cards = db.query(BankCard).filter(BankCard.payment_method_id == method_id).all()
                        
                        message = "💳 لیست کارت‌های بانکی:\n\n"
                        buttons = []
                        
                        for card in cards:
                            # نمایش ۴ رقم آخر کارت
                            masked_number = f"•••• •••• •••• {card.card_number[-4:]}"
                            buttons.extend([
                                [Button.inline(f"{masked_number} - {card.bank_name}", f"view_card_{card.id}")],
                                [
                                    Button.inline("✏️ ویرایش", f"edit_card_{card.id}"),
                                    Button.inline("❌ حذف", f"delete_card_{card.id}")
                                ]
                            ])
                        
                        buttons.extend([
                            [Button.inline("➕ افزودن کارت جدید", f"add_card_{method_id}")],
                            [Button.inline("🔙 بازگشت", "back_to_payment_methods")]
                        ])
                        
                    else:
                        # نمایش اطلاعات سایر متدها
                        message = f"💳 {method.name}\n\n"
                        message += f"توضیحات: {method.description}\n"
                        
                        buttons = [
                            [
                                Button.inline("✏️ ویرایش", f"edit_method_{method_id}"),
                                Button.inline("❌ حذف", f"delete_method_{method_id}")
                            ],
                            [Button.inline("🔙 بازگشت", "back_to_payment_methods")]
                        ]

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in view_payment_method: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"add_card_\d+"))
        async def start_add_card(event):
            """Start process of adding new bank card"""
            try:
                method_id = int(event.data.decode().split('_')[2])
                user_id = event.sender_id
                
                self.user_states[user_id] = {
                    "action": "add_card",
                    "method_id": method_id,
                    "step": "number"
                }
                
                await event.edit(
                    "لطفاً شماره کارت را وارد کنید (۱۶ رقم بدون فاصله):",
                    buttons=[[Button.inline("🔙 انصراف", "cancel_card_add")]]
                )

            except Exception as e:
                logger.error(f"Error in start_add_card: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_payment_method"))
        async def start_add_payment_method(event):
            """Start process of adding new payment method"""
            try:
                user_id = event.sender_id
                
                message = "لطفاً نوع روش پرداخت را انتخاب کنید:"
                buttons = [
                    [Button.inline("💳 افزودن کارت بانکی", "add_bank_card_method")],
                    [Button.inline("💎 افزودن آدرس کریپتو", "add_crypto_method")],
                    [Button.inline("🔙 بازگشت", "back_to_payment_methods")]
                ]
                
                await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in start_add_payment_method: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_bank_card_method"))
        async def start_add_bank_card(event):
            """Start process of adding new bank card method"""
            try:
                user_id = event.sender_id
                self.user_states[user_id] = {
                    "action": "add_bank_card",
                    "step": "card_number"
                }
                
                await event.edit(
                    "لطفاً شماره کارت را وارد کنید (۱۶ رقم بدون فاصله):",
                    buttons=[[Button.inline("🔙 انصراف", "cancel_add_method")]]
                )

            except Exception as e:
                logger.error(f"Error in start_add_bank_card: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_crypto_method"))
        async def start_add_crypto(event):
            """Start process of adding new crypto wallet"""
            try:
                user_id = event.sender_id
                self.user_states[user_id] = {
                    "action": "add_crypto",
                    "step": "wallet_address"
                }
                
                await event.edit(
                    "لطفاً آدرس کیف پول کریپتو را وارد کنید:",
                    buttons=[[Button.inline("🔙 انصراف", "cancel_add_method")]]
                )

            except Exception as e:
                logger.error(f"Error in start_add_crypto: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_payment_method_input(event):
            """Handle input for payment method creation"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state:
                return

            try:
                if state["action"] == "add_bank_card":
                    if state["step"] == "card_number":
                        card_number = event.text.strip()
                        if len(card_number) != 16 or not card_number.isdigit():
                            await event.respond("❌ شماره کارت نامعتبر است. لطفاً مجدداً وارد کنید:")
                            return
                        
                        state["card_number"] = card_number
                        state["step"] = "card_holder"
                        await event.respond("لطفاً نام صاحب کارت را وارد کنید:")

                    elif state["step"] == "card_holder":
                        card_holder = event.text.strip()
                        if len(card_holder) < 3:
                            await event.respond("❌ نام صاحب کارت نامعتبر است. لطفاً مجدداً وارد کنید:")
                            return
                        
                        # Save to database
                        with SessionLocal() as db:
                            method = PaymentMethod(
                                name=f"Bank Card - {card_holder}",
                                type="CARD",
                                description=f"Card ending in {state['card_number'][-4:]}"
                            )
                            db.add(method)
                            db.flush()
                            
                            card = BankCard(
                                payment_method_id=method.id,
                                card_number=state["card_number"],
                                card_holder=card_holder
                            )
                            db.add(card)
                            db.commit()
                        
                        del self.user_states[user_id]
                        await event.respond(
                            "✅ کارت بانکی با موفقیت اضافه شد.",
                            buttons=[[Button.inline("🔙 بازگشت به لیست", "payment_methods")]]
                        )

                elif state["action"] == "add_crypto":
                    if state["step"] == "wallet_address":
                        wallet_address = event.text.strip()
                        if len(wallet_address) < 20:  # Basic validation
                            await event.respond("❌ آدرس کیف پول نامعتبر است. لطفاً مجدداً وارد کنید:")
                            return
                        
                        # Save to database
                        with SessionLocal() as db:
                            method = PaymentMethod(
                                name="Crypto Wallet",
                                type="CRYPTO",
                                description=f"Wallet: {wallet_address}"
                            )
                            db.add(method)
                            db.commit()
                        
                        del self.user_states[user_id]
                        await event.respond(
                            "✅ آدرس کیف پول با موفقیت اضافه شد.",
                            buttons=[[Button.inline("🔙 بازگشت به لیست", "payment_methods")]]
                        )

            except Exception as e:
                logger.error(f"Error in handle_payment_method_input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

        @self.client.on(events.CallbackQuery(pattern="cancel_add_method"))
        async def cancel_add_method(event):
            """Cancel payment method addition"""
            try:
                user_id = event.sender_id
                if user_id in self.user_states:
                    del self.user_states[user_id]
                
                await event.edit(
                    "❌ عملیات لغو شد.",
                    buttons=[[Button.inline("🔙 بازگشت به لیست", "payment_methods")]]
                )

            except Exception as e:
                logger.error(f"Error in cancel_add_method: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        # ... سایر هندلرها برای ویرایش و حذف کارت‌ها ...

