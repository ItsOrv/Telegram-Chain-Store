from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import Order, MainLocation, Notification, OrderStatus, User
from src.bot.common.messages import Messages
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class DeliveryHandler:
    def __init__(self, client):
        self.client = client
        self.user_states = {}  # اضافه کردن user_states به کلاس
        self.settings = get_settings()
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern=r"set_mainloc_\d+"))
        async def handle_set_mainlocation(event):
            """فروشنده مکان نهایی تحویل را ثبت می‌کند"""
            try:
                order_id = int(event.data.decode().split('_')[2])
                user_id = event.sender_id

                # استفاده از self.user_states به جای self.client.user_states
                self.user_states[user_id] = {
                    "action": "set_mainloc",
                    "order_id": order_id,
                    "step": "enter_address"
                }

                await event.edit(
                    "📍 لطفاً آدرس دقیق محل تحویل را وارد کنید:",
                    buttons=[[Button.inline("🔙 انصراف", "cancel_mainloc")]]
                )

            except Exception as e:
                logger.error(f"Error in handle_set_mainlocation: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_mainlocation_input(event):
            """پردازش ورودی آدرس نهایی از فروشنده"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)  # استفاده از self.user_states

            if not state or state.get("action") != "set_mainloc":
                return

            try:
                address = event.text.strip()
                order_id = state["order_id"]

                with SessionLocal() as db:
                    # ذخیره آدرس نهایی
                    main_location = MainLocation(
                        order_id=order_id,
                        address=address,
                        status='PENDING'  # نیاز به تایید ادمین
                    )
                    db.add(main_location)

                    # بروزرسانی وضعیت سفارش
                    order = db.query(Order).get(order_id)
                    order.status = OrderStatus.PENDING_ADMIN_CONFIRMATION
                    
                    # ارسال نوتیفیکیشن به ادمین
                    admin_notif = Notification(
                        user_id=self.settings.HEAD_ADMIN_ID,
                        title="🏠 درخواست تایید آدرس نهایی",
                        message=f"سفارش: {order_id}\nآدرس: {address}"
                    )
                    db.add(admin_notif)
                    
                    # ارسال نوتیفیکیشن به خریدار
                    buyer_notif = Notification(
                        user_id=order.buyer_id,
                        title="📍 ثبت آدرس تحویل",
                        message="آدرس تحویل توسط فروشنده ثبت شد و در انتظار تایید است."
                    )
                    db.add(buyer_notif)
                    
                    db.commit()

                    # ارسال پیام به ادمین برای تایید
                    admin_message = (
                        f"🏠 درخواست تایید آدرس نهایی:\n\n"
                        f"سفارش: {order_id}\n"
                        f"آدرس: {address}"
                    )
                    
                    admin_buttons = [
                        [
                            Button.inline("✅ تایید", f"approve_mainloc_{main_location.id}"),
                            Button.inline("❌ رد", f"reject_mainloc_{main_location.id}")
                        ]
                    ]

                    await self.client.send_message(
                        self.settings.HEAD_ADMIN_ID,
                        admin_message,
                        buttons=admin_buttons
                    )

                    # پاسخ به فروشنده
                    await event.respond(
                        "✅ آدرس با موفقیت ثبت شد و برای تایید به ادمین ارسال شد."
                    )

                    # پاک کردن state
                    del self.user_states[user_id]  # استفاده از self.user_states

            except Exception as e:
                logger.error(f"Error in handle_mainlocation_input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

        @self.client.on(events.CallbackQuery(pattern=r"approve_mainloc_\d+"))
        async def handle_approve_mainlocation(event):
            """تایید آدرس نهایی توسط ادمین"""
            try:
                if str(event.sender_id) != str(self.settings.HEAD_ADMIN_ID):
                    await event.answer("⛔️ شما دسترسی به این عملیات را ندارید!", alert=True)
                    return

                location_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    main_location = db.query(MainLocation).get(location_id)
                    if not main_location:
                        await event.answer("❌ آدرس یافت نشد!", alert=True)
                        return

                    # تایید آدرس
                    main_location.status = 'APPROVED'
                    
                    # بروزرسانی وضعیت سفارش
                    order = main_location.order
                    order.status = OrderStatus.AT_PUBLIC_LOCATION_PENDING_PICKUP
                    order.final_shipping_address = main_location.address

                    # ارسال نوتیفیکیشن به خریدار
                    buyer_notif = Notification(
                        user_id=order.buyer_id,
                        title="✅ تایید آدرس تحویل",
                        message=f"آدرس تحویل تایید شد:\n{main_location.address}"
                    )
                    db.add(buyer_notif)

                    # ارسال نوتیفیکیشن به فروشنده
                    seller_notif = Notification(
                        user_id=order.product.seller_id,
                        title="✅ تایید آدرس تحویل",
                        message="آدرس تحویل توسط ادمین تایید شد."
                    )
                    db.add(seller_notif)
                    
                    db.commit()

                    # ارسال آدرس به خریدار
                    await self.client.send_message(
                        order.buyer.telegram_id,
                        f"📍 آدرس تحویل سفارش {order.id}:\n\n"
                        f"{main_location.address}\n\n"
                        "پس از دریافت محصول، لطفاً با دکمه زیر آن را تایید کنید.",
                        buttons=[[Button.inline("✅ دریافت شد", f"confirm_delivery_{order.id}")]]
                    )

                    # پاسخ به ادمین
                    await event.edit(
                        event.message.text + "\n\n✅ تایید شده",
                        buttons=None
                    )

            except Exception as e:
                logger.error(f"Error in handle_approve_mainlocation: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"reject_mainloc_\d+"))
        async def handle_reject_mainlocation(event):
            """رد آدرس نهایی توسط ادمین"""
            # مشابه handle_approve_mainlocation با تغییر وضعیت به REJECTED
            # ...

        @self.client.on(events.CallbackQuery(pattern=r"confirm_delivery_\d+"))
        async def handle_confirm_delivery(event):
            """تایید دریافت محصول توسط خریدار"""
            try:
                order_id = int(event.data.decode().split('_')[2])
                user_id = event.sender_id

                with SessionLocal() as db:
                    order = db.query(Order).get(order_id)
                    if not order or order.buyer.telegram_id != user_id:
                        await event.answer("❌ سفارش نامعتبر!", alert=True)
                        return

                    # تکمیل سفارش
                    order.status = OrderStatus.COMPLETED

                    # ارسال نوتیفیکیشن به فروشنده
                    seller_notif = Notification(
                        user_id=order.product.seller_id,
                        title="✅ تحویل موفق",
                        message=f"سفارش {order.id} با موفقیت تحویل داده شد."
                    )
                    db.add(seller_notif)
                    
                    db.commit()

                    # پاسخ به خریدار
                    await event.edit(
                        "✅ دریافت سفارش با موفقیت تایید شد.\n"
                        "با تشکر از خرید شما!",
                        buttons=[[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]
                    )

            except Exception as e:
                logger.error(f"Error in handle_confirm_delivery: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

