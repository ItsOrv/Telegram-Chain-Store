from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, Province, City, UserCity, UserRole, PreLocation, MainLocation, Order, Notification
from typing import List, Dict
from src.bot.common.messages import Messages
from src.bot.common.keyboards import get_role_keyboard
from src.bot.common.keyboards import LocationKeyboards  # Add this import
import logging

logger = logging.getLogger(__name__)

class LocationHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern=r"province_\d+"))
        async def handle_province_selection(event):
            province_id = int(event.data.decode().split('_')[1])
            user_id = event.sender_id
            
            # Save selected province in state
            self.user_states[user_id] = {"province_id": province_id}
            
            # Show cities of selected province
            await self.show_cities(event, province_id)

        @self.client.on(events.CallbackQuery(pattern=r"city_\d+"))
        async def handle_city_selection(event):
            city_id = int(event.data.decode().split('_')[1])
            user_id = event.sender_id
            
            # Save location to database
            await self.save_user_location(event, user_id, city_id)

        @self.client.on(events.CallbackQuery(pattern="📍 Change My Location"))
        async def handle_change_location(event):
            """Handle change location button click"""
            user_id = event.sender_id
            
            with SessionLocal() as db:
                # Get user and clear their location
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await event.answer(Messages.UNAUTHORIZED, alert=True)
                    return

                # Check if user is not admin
                if user.role == UserRole.ADMIN:
                    await event.answer("Admins don't need to set location", alert=True)
                    return

                # Clear existing user_cities
                db.query(UserCity).filter(UserCity.user_id == user.id).delete()
                db.commit()

                # Start location selection process
                await event.delete()  # Delete the menu message
                await self.show_provinces(event)

        @self.client.on(events.CallbackQuery(pattern=r"order_location_\d+"))
        async def handle_order_location(event):
            """مدیریت انتخاب لوکیشن برای سفارش"""
            try:
                order_id = int(event.data.decode().split('_')[2])
                with SessionLocal() as db:
                    order = db.query(Order).get(order_id)
                    if not order:
                        await event.answer("سفارش یافت نشد!", alert=True)
                        return

                    # دریافت pre-locations موجود
                    pre_locations = db.query(PreLocation).filter(
                        PreLocation.city_id == order.product.city_id,
                        PreLocation.is_active == True
                    ).all()

                    if not pre_locations:
                        # درخواست اضافه کردن pre-location به ادمین
                        await self.request_new_prelocation(event, order)
                        return

                    # نمایش لیست pre-locations
                    message = "📍 لطفاً یک مکان عمومی را انتخاب کنید:"
                    buttons = LocationKeyboards.get_pre_locations(pre_locations, order_id)
                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_order_location: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"select_preloc_\d+_\d+"))
        async def handle_prelocation_selection(event):
            """مدیریت انتخاب pre-location"""
            try:
                order_id, loc_id = map(int, event.data.decode().split('_')[2:])
                
                with SessionLocal() as db:
                    order = db.query(Order).get(order_id)
                    location = db.query(PreLocation).get(loc_id)
                    
                    if not order or not location:
                        await event.answer("خطا در انتخاب مکان!", alert=True)
                        return

                    # ذخیره pre-location در سفارش
                    order.pre_shipping_address = location.address
                    db.commit()

                    # ارسال نوتیفیکیشن به فروشنده
                    seller_notif = Notification(
                        user_id=order.product.seller_id,
                        title="📍 انتخاب مکان تحویل",
                        message=(
                            f"مکان تحویل برای سفارش {order.id}:\n"
                            f"مکان: {location.name}\n"
                            f"آدرس: {location.address}"
                        )
                    )
                    db.add(seller_notif)
                    db.commit()

                    # ارسال پیام به فروشنده
                    await self.client.send_message(
                        order.product.seller.telegram_id,
                        f"📍 مکان تحویل انتخاب شد:\n\n"
                        f"سفارش: {order.id}\n"
                        f"مکان: {location.name}\n"
                        f"آدرس: {location.address}",
                        buttons=[[
                            Button.inline(
                                "✅ ثبت مکان تحویل نهایی",
                                f"set_mainloc_{order.id}"
                            )
                        ]]
                    )

                    await event.edit(
                        "✅ مکان تحویل با موفقیت ثبت شد\n"
                        "لطفاً منتظر تایید و ارسال آدرس نهایی توسط فروشنده باشید.",
                        buttons=[[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]
                    )

            except Exception as e:
                logger.error(f"Error in handle_prelocation_selection: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def check_user_location(self, event) -> bool:
        """Check if user has set their location"""
        user_id = event.sender_id
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user or not user.cities:
                await self.show_provinces(event)
                return False
            return True

    async def show_provinces(self, event):
        """Show list of provinces as inline buttons"""
        with SessionLocal() as db:
            provinces = db.query(Province).all()
            if not provinces:
                await event.respond("No provinces found!")
                return
                
            buttons = LocationKeyboards.get_provinces(provinces)
            await event.respond(Messages.SELECT_PROVINCE, buttons=buttons)

    async def show_cities(self, event, province_id: int):
        """Show cities of selected province"""
        with SessionLocal() as db:
            cities = db.query(City).filter(City.province_id == province_id).all()
            if not cities:
                await event.respond("No cities found for this province!")
                return
                
            buttons = LocationKeyboards.get_cities(cities)
            await event.edit(Messages.SELECT_CITY, buttons=buttons)

    async def save_user_location(self, event, user_id: int, city_id: int):
        """Save user's selected city to database"""
        with SessionLocal() as db:
            # Get user
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                await event.answer(Messages.UNAUTHORIZED, alert=True)
                return

            # Get city and province info
            city = db.query(City).filter(City.id == city_id).first()
            
            # Clear existing user_cities
            db.query(UserCity).filter(UserCity.user_id == user.id).delete()
            
            # Create new user_city record
            user_city = UserCity(user_id=user.id, city_id=city_id)
            db.add(user_city)
            
            try:
                db.commit()
                # Show success message
                await event.edit(
                    Messages.LOCATION_UPDATED.format(
                        city=city.name,
                        province=city.province.name
                    )
                )
                
                # Show start menu after location is set
                await event.respond(
                    Messages.WELCOME_BACK.format(
                        username=user.username,
                        role=user.role.lower()
                    ),
                    buttons=get_role_keyboard(user.role.lower())
                )
                
            except Exception as e:
                db.rollback()
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def request_new_prelocation(self, event, order):
        """درخواست اضافه کردن pre-location جدید از ادمین"""
        try:
            # ارسال درخواست به ادمین
            admin_message = (
                f"⚠️ درخواست اضافه کردن مکان عمومی جدید:\n\n"
                f"شهر: {order.product.city.name}\n"
                f"سفارش: {order.id}"
            )
            
            await self.client.send_message(
                self.settings.HEAD_ADMIN_ID,
                admin_message,
                buttons=[[
                    Button.inline(
                        "➕ افزودن مکان جدید",
                        f"add_preloc_{order.product.city_id}"
                    )
                ]]
            )

            # اطلاع به کاربر
            await event.edit(
                "⚠️ در حال حاضر مکان عمومی در این شهر تعریف نشده است.\n"
                "درخواست شما به ادمین ارسال شد.\n"
                "لطفاً منتظر بمانید.",
                buttons=[[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]
            )

        except Exception as e:
            logger.error(f"Error in request_new_prelocation: {e}")
            await event.answer(Messages.ERROR_OCCURRED, alert=True)
