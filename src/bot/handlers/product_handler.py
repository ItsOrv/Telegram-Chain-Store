from telethon import events, Button
from src.bot.common.keyboards import get_role_keyboard
from src.core.database import SessionLocal
from src.core.models import CartItem, User, Product, Category, City, Province, ProductImage, UserCity, UserRole
from src.bot.common.messages import Messages
from decimal import Decimal
from typing import Dict, Any, List
import logging
from sqlalchemy import func
from datetime import datetime
from src.core.exceptions import ValidationError, ProductError
from src.core.services.order_manager import OrderManager

logger = logging.getLogger(__name__)

class ProductHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.last_message_ids: Dict[int, int] = {}  # Add this to store last message IDs
        self.order_manager = OrderManager()
        self.setup_handlers()

    # اضافه کردن متد کمکی برای بروزرسانی پیام مشتری
    async def update_customer_products_message(self, user_id, chat_id):
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not user:
                return None
            user_city = db.query(UserCity).filter(UserCity.user_id == user.id).first()
            if not user_city:
                return None
            
            # دریافت آیتم‌های سبد خرید
            cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
            cart_dict = {item.product_id: item.quantity for item in cart_items}
            
            # محاسبه جمع کل سبد خرید و گرد کردن به عدد صحیح
            total_amount = int(sum(item.quantity * item.product.price for item in cart_items))

            # دریافت محصولات فعال در شهر کاربر
            products = db.query(Product).filter(
                Product.city_id == user_city.city_id,
                Product.status == 'active',
                Product.deleted_at.is_(None)
            ).order_by(Product.created_at.desc()).all()

            city = db.query(City).get(user_city.city_id)

            # ساخت پیام و دکمه‌ها
            message_lines = [
                f"🛍 محصولات موجود در {city.name}",
                f"💰 جمع سبد خرید: {int(total_amount):,} تومان" if total_amount > 0 else "🛒 سبد خرید شما خالی است",
                "━━━━━━━━━━━━━━━"
            ]

            buttons = []
            if products:
                # نمایش محصولات
                for product in products:
                    current_qty = cart_dict.get(product.id, 0)
                    
                    # افزودن محصول به پیام
                    buttons.extend([
                        [Button.inline(f"{product.name} - {int(product.price):,} تومان", f"view_{product.id}")],
                        [Button.inline("➖", f"decrease_{product.id}"),
                         Button.inline(f"🛒 {current_qty}", f"qty_{product.id}"),
                         Button.inline("➕", f"increase_{product.id}")]
                    ])
                    
                    # اگر محصول در سبد خرید هست، اطلاعات آن را نمایش بده
                    if current_qty > 0:
                        message_lines.extend([
                            f"\n📦 {product.name}",
                            f"💰 قیمت: {int(product.price):,} تومان",
                            f"🛒 تعداد در سبد: {current_qty}",
                            f"💵 جمع: {int(current_qty * product.price):,} تومان",
                            f"{'━' * 20}"
                        ])

                buttons.extend([
                    [Button.inline("━━━━━━━━━━", "none")],
                    [Button.inline("🔄 تکمیل خرید", "next_step")] if total_amount > 0 else [],  # تغییر به next_step
                    [Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]
                ])
            else:
                message_lines.append("\n❌ محصولی در این شهر موجود نیست")
                buttons = [[Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]]

            text = "\n".join(message_lines)
            return (text, buttons)

    async def update_cart_message(self, user_id, chat_id):
        """Update cart message with only non-zero quantity items"""
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not user:
                return None
                
            # دریافت آیتم‌های سبد خرید
            cart_items = db.query(CartItem).filter(
                CartItem.user_id == user.id,
                CartItem.quantity > 0  # فقط محصولات با تعداد بیشتر از صفر
            ).all()
            
            cart_dict = {item.product_id: item.quantity for item in cart_items}
            total_amount = int(sum(item.quantity * item.product.price for item in cart_items))

            # ساخت پیام و دکمه‌ها
            message_lines = [
                "🛒 سبد خرید شما:",
                f"💰 مجموع: {total_amount:,} تومان",
                "━━━━━━━━━━━━━━━"
            ]

            buttons = []
            
            # نمایش فقط محصولات موجود در سبد خرید
            for cart_item in cart_items:
                product = cart_item.product
                current_qty = cart_dict.get(product.id, 0)
                
                if current_qty > 0:
                    message_lines.extend([
                        f"\n📦 {product.name}",
                        f"💰 قیمت واحد: {int(product.price):,} تومان",
                        f"🛒 تعداد: {current_qty}",
                        f"💵 جمع: {int(current_qty * product.price):,} تومان",
                        f"{'━' * 20}"
                    ])
                    
                    buttons.extend([
                        [Button.inline(f"{product.name} - {int(product.price):,} تومان", f"view_{product.id}")],
                        [Button.inline("➖", f"decrease_{product.id}"),
                         Button.inline(f"🛒 {current_qty}", f"qty_{product.id}"),
                         Button.inline("➕", f"increase_{product.id}")]
                    ])

            # اضافه کردن دکمه‌های پایینی
            buttons.extend([
                [Button.inline("━━━━━━━━━━", "none")],
                [Button.inline("🔄 مرحله بعد", "next_step")] if total_amount > 0 else [],  # تغییر به next_step
                [Button.inline("🗑 خالی کردن سبد خرید", "clear_cart")],
                [Button.inline("🏠 بازگشت به منوی اصلی", "back_to_main")]
            ])

            text = "\n".join(message_lines)
            return (text, buttons)

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern=r"🛍 Manage Products|🛍 Manage My Products"))
        async def show_products_list(event):
            """Show products list based on user role"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                    # Get products based on role
                    if user.role == UserRole.ADMIN:
                        # Admin sees all products
                        products = db.query(Product).filter(
                            Product.deleted_at.is_(None)
                        ).order_by(Product.created_at.desc()).all()
                        
                        message = "📋 لیست تمام محصولات:\n\n"
                        
                    elif user.role == UserRole.SELLER:
                        # Seller sees only their products
                        products = db.query(Product).filter(
                            Product.seller_id == user.id,
                            Product.deleted_at.is_(None)
                        ).order_by(Product.created_at.desc()).all()
                        
                        message = "📋 لیست محصولات شما:\n\n"
                    
                    else:
                        await event.answer("⛔️ شما دسترسی به این بخش را ندارید!", alert=True)
                        return

                    # Create message and buttons
                    if products:
                        buttons = []
                        for product in products:
                            product_info = (
                                f"📦 {product.name}\n"
                                f"💰 قیمت: {int(product.price):,} تومان\n"
                                f"📊 موجودی: {product.stock}\n"
                                f"📍 {product.city.name}\n"
                                f"{'─' * 20}\n"
                            )
                            message += product_info
                            
                            # Add management buttons for each product
                            buttons.extend([
                                [Button.inline(f"📦 {product.name}", f"view_product_{product.id}")],
                                [
                                    Button.inline("✏️ ویرایش", f"edit_product_{product.id}"),
                                    Button.inline("❌ حذف", f"delete_product_{product.id}")
                                ]
                            ])
                    else:
                        message = "❌ هیچ محصولی یافت نشد."
                        buttons = []

                    # Add common buttons
                    buttons.extend([
                        [Button.inline("➕ افزودن محصول جدید", "add_product")],
                        [Button.inline("🔙 بازگشت به منوی اصلی", "back_to_main")]
                    ])

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in show_products_list: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"view_product_\d+"))
        async def handle_product_view(event):
            """نمایش جزئیات محصول"""
            try:
                product_id = int(event.data.decode().split('_')[2])
                user_id = event.sender_id
                
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    product = db.query(Product).get(product_id)
                    
                    if not product:
                        await event.answer("❌ محصول یافت نشد!", alert=True)
                        return
                        
                    # Check permissions
                    if user.role == UserRole.SELLER and product.seller_id != user.id:
                        await event.answer("⛔️ شما دسترسی به این محصول را ندارید!", alert=True)
                        return

                    # Create detailed message
                    message = (
                        f"📦 {product.name}\n\n"
                        f"📝 توضیحات: {product.description or 'بدون توضیحات'}\n"
                        f"💰 قیمت: {int(product.price):,} تومان\n"
                        f"📊 موجودی: {product.stock}\n"
                        f"⚖️ وزن: {product.weight or 'نامشخص'} گرم\n"
                        f"🏢 دسته‌بندی: {product.category.name}\n"
                        f"📍 شهر: {product.city.name}\n"
                        f"🏠 منطقه: {product.zone or 'نامشخص'}\n"
                        f"📅 تاریخ ثبت: {product.created_at.strftime('%Y-%m-%d')}\n"
                        f"⚡️ وضعیت: {product.status}\n"
                    )

                    buttons = [
                        [
                            Button.inline("✏️ ویرایش", f"edit_product_{product.id}"),
                            Button.inline("❌ حذف", f"delete_product_{product.id}")
                        ],
                        [Button.inline("🔙 بازگشت به لیست", "back_to_products")]
                    ]

                    await event.edit(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in handle_product_view: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_product"))
        async def start_add_product(event):
            """Start product creation process"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    seller = db.query(User).filter(
                        User.telegram_id == str(user_id),
                        User.role == "SELLER"
                    ).first()
                    
                    if not seller:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                # Initialize product creation state
                self.user_states[user_id] = {
                    "action": "add_product",
                    "step": "name",
                    "data": {}
                }
                
                # Start with product name
                await event.edit(Messages.ADD_PRODUCT_NAME)

            except Exception as e:
                logger.error(f"Error in start_add_product: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="cancel_product_add"))
        async def cancel_product_add(event):
            """Cancel product addition process"""
            try:
                user_id = event.sender_id
                # Clear user state
                if user_id in self.user_states:
                    del self.user_states[user_id]
                
                # Show main menu
                with SessionLocal() as db:
                    seller = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if seller:
                        await event.edit(
                            Messages.ADD_PRODUCT_CANCELLED,
                            buttons=get_role_keyboard(seller.role.lower())
                        )
            except Exception as e:
                logger.error(f"Error in cancel_product_add: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_product_input(event):
            """Handle product creation input"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state or state["action"] != "add_product":
                return

            try:
                step = state["step"]
                data = state["data"]

                # Create cancel button
                cancel_button = [[Button.inline("❌ Cancel", "cancel_product_add")]]

                if step == "name":
                    data["name"] = event.text
                    state["step"] = "description"
                    await event.respond(Messages.ADD_PRODUCT_DESCRIPTION, buttons=cancel_button)

                elif step == "description":
                    data["description"] = event.text
                    state["step"] = "price"
                    await event.respond(Messages.ADD_PRODUCT_PRICE, buttons=cancel_button)

                elif step == "price":
                    try:
                        price = Decimal(event.text)
                        if price <= 0:
                            raise ValueError("Price must be positive")
                        data["price"] = price
                        state["step"] = "stock"
                        await event.respond(Messages.ADD_PRODUCT_STOCK, buttons=cancel_button)
                    except:
                        await event.respond(Messages.INVALID_PRICE, buttons=cancel_button)
                        return

                elif step == "stock":
                    try:
                        stock = int(event.text)
                        if stock < 0:
                            raise ValueError("Stock cannot be negative")
                        data["stock"] = stock
                        state["step"] = "weight"
                        await event.respond(Messages.ADD_PRODUCT_WEIGHT, buttons=cancel_button)
                    except:
                        await event.respond(Messages.INVALID_NUMBER, buttons=cancel_button)
                        return

                elif step == "weight":
                    try:
                        weight = int(event.text)  # Get weight directly in grams
                        if weight <= 0:
                            raise ValueValueError("Weight must be positive")
                        data["weight"] = weight
                        state["step"] = "province"
                        await self.show_provinces(event)
                    except:
                        await event.respond(Messages.INVALID_NUMBER, buttons=cancel_button)
                        return

                elif step == "province":
                    try:
                        province_id = int(event.text)
                        with SessionLocal() as db:
                            province = db.query(Province).get(province_id)
                            if not province:
                                raise ValueError("Invalid province")
                            data["province_id"] = province_id
                            state["step"] = "city"
                            await self.show_cities(event, province_id)
                    except:
                        await event.respond(Messages.INVALID_PROVINCE, buttons=cancel_button)
                        return

                elif step == "city":
                    try:
                        city_id = int(event.text)
                        with SessionLocal() as db:
                            city = db.query(City).get(city_id)
                            if not city:
                                raise ValueError("Invalid city")
                            data["city_id"] = city_id
                            state["step"] = "category"
                            await self.show_categories(event)
                    except:
                        await event.respond(Messages.INVALID_CITY, buttons=cancel_button)
                        return

                elif step == "category":
                    try:
                        category_id = int(event.text)
                        with SessionLocal() as db:
                            category = db.query(Category).get(category_id)
                            if not category:
                                raise ValueError("Invalid category")
                            data["category_id"] = category_id
                            state["step"] = "zone"
                            await event.respond(Messages.ADD_PRODUCT_ZONE, buttons=cancel_button)
                    except:
                        await event.respond(Messages.INVALID_CATEGORY, buttons=cancel_button)
                        return

                elif step == "zone":
                    data["zone"] = event.text
                    state["step"] = "image"
                    await event.respond(Messages.ADD_PRODUCT_IMAGE, buttons=cancel_button)

                elif step == "image":
                    if event.photo:
                        path = await event.download_media()
                        data["image"] = path
                        await self.save_product(event, user_id, data)
                    else:
                        await event.respond(Messages.INVALID_IMAGE, buttons=cancel_button)

            except Exception as e:
                logger.error(f"Error in handle_product_input: {e}")
                await event.respond(Messages.ERROR_OCCURRED, buttons=cancel_button)

        @self.client.on(events.CallbackQuery(pattern=r"select_category_\d+"))
        async def handle_category_selection(event):
            """Handle category selection for product creation"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or state["action"] != "add_product":
                    return

                # Extract category ID from callback data
                category_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    # Verify category exists
                    category = db.query(Category).get(category_id)
                    if not category:
                        await event.answer(Messages.INVALID_CATEGORY, alert=True)
                        return
                    
                    # Save category ID in state
                    state["data"]["category_id"] = category_id
                    
                    # Move to next step (zone)
                    state["step"] = "zone"
                    await event.edit(
                        Messages.ADD_PRODUCT_ZONE,
                        buttons=[[Button.inline("❌ Cancel", "cancel_product_add")]]
                    )

            except Exception as e:
                logger.error(f"Error in handle_category_selection: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_products"))
        async def handle_back_to_products(event):
            """Handle back to products list button"""
            try:
                await self.show_products_list(event)
            except Exception as e:
                logger.error(f"Error in handle_back_to_products: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"product_province_\d+"))  # Changed pattern
        async def handle_province_selection(event):
            """Handle province selection for product"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or state["action"] != "add_product":
                    return

                # Extract province ID from callback data
                province_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    province = db.query(Province).get(province_id)
                    if not province:
                        await event.answer(Messages.INVALID_PROVINCE, alert=True)
                        return
                    
                    state["data"]["province_id"] = province_id
                    await self.show_cities(event, province_id)

            except Exception as e:
                logger.error(f"Error in handle_province_selection: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"product_city_\d+"))  # Changed pattern
        async def handle_city_selection(event):
            """Handle city selection for product"""
            try:
                user_id = event.sender_id
                state = self.user_states.get(user_id)
                
                if not state or state["action"] != "add_product":
                    return

                # Extract city ID from callback data
                city_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    city = db.query(City).get(city_id)
                    if not city:
                        await event.answer(Messages.INVALID_CITY, alert=True)
                        return
                    
                    state["data"]["city_id"] = city_id
                    state["step"] = "category"
                    await self.show_categories(event)

            except Exception as e:
                logger.error(f"Error in handle_city_selection: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="🛒 Product List"))
        async def show_customer_products_list(event):
            """Show available products for customer's city"""
            try:
                user_id = event.sender_id
                chat_id = event.chat_id
                # حذف پیام قبلی در صورت وجود
                old_msg_id = self.last_message_ids.get(user_id)
                if old_msg_id:
                    try:
                        await self.client.delete_messages(chat_id, old_msg_id)
                    except:
                        pass
                res = await self.update_customer_products_message(user_id, chat_id)
                if res:
                    text, buttons = res
                    new_msg = await event.respond(text, buttons=buttons)
                    self.last_message_ids[user_id] = new_msg.id
                    await event.delete()
            except Exception as e:
                logger.error(f"Error in show_customer_products_list: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"(increase|decrease)_\d+"))
        async def handle_quantity_change(event):
            """Handle increasing/decreasing product quantity and update persistent message"""
            try:
                data = event.data.decode()
                action, prod_id_str = data.split('_')
                product_id = int(prod_id_str)
                user_id = event.sender_id
                chat_id = event.chat_id

                with SessionLocal() as db:
                    # دریافت کاربر و ذخیره شناسه
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return
                    local_user_id = user.id   # ذخیره id کاربر به صورت محلی
                    user_city = db.query(UserCity).filter(UserCity.user_id == local_user_id).first()
                    if not user_city:
                        await event.answer(Messages.NO_LOCATION_SET, alert=True)
                        return
                    # بروزرسانی تعداد محصول
                    selected_product = db.query(Product).get(product_id)
                    if not selected_product:
                        await event.answer(Messages.PRODUCT_NOT_FOUND, alert=True)
                        return
                    cart_item = db.query(CartItem).filter(
                        CartItem.user_id == local_user_id,
                        CartItem.product_id == product_id
                    ).first()
                    if action == "increase":
                        if not cart_item:
                            if selected_product.stock <= 0:
                                await event.answer(Messages.OUT_OF_STOCK, alert=True)
                                return
                            cart_item = CartItem(user_id=local_user_id, product_id=product_id, quantity=0)
                            db.add(cart_item)
                        if cart_item.quantity >= selected_product.stock:
                            await event.answer(Messages.EXCEEDS_STOCK, alert=True)
                            return
                        cart_item.quantity += 1
                    elif action == "decrease":
                        if cart_item:
                            if cart_item.quantity > 1:
                                cart_item.quantity -= 1
                            else:
                                db.delete(cart_item)
                    db.commit()

                    # بروزرسانی پیام ثابت نمایش محصولات
                    res = await self.update_customer_products_message(user_id, chat_id)
                    if res:
                        text, buttons = res
                        msg_id = self.last_message_ids.get(user_id)
                        if msg_id:
                            try:
                                await self.client.edit_message(chat_id, msg_id, text, buttons=buttons)
                            except Exception:
                                new_msg = await event.respond(text, buttons=buttons)
                                self.last_message_ids[user_id] = new_msg.id
                        else:
                            new_msg = await event.respond(text, buttons=buttons)
                            self.last_message_ids[user_id] = new_msg.id

                    await event.answer()  # پاسخ خالی برای بستن loading indicator

            except Exception as e:
                logger.error(f"Error in handle_quantity_change: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="🛍 Show Cart"))
        async def show_cart(event):
            """Show user's cart with non-zero quantity items"""
            try:
                user_id = event.sender_id
                chat_id = event.chat_id
                
                res = await self.update_cart_message(user_id, chat_id)
                if res:
                    text, buttons = res
                    await event.edit(text, buttons=buttons)
                    
            except Exception as e:
                logger.error(f"Error in show_cart: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="clear_cart"))
        async def clear_cart(event):
            """Clear all items from user's cart"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return
                    
                    # حذف همه آیتم‌های سبد خرید
                    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
                    db.commit()
                    
                    await event.answer("✅ سبد خرید شما با موفقیت خالی شد.", alert=True)
                    
                    # بروزرسانی نمایش سبد خرید
                    chat_id = event.chat_id
                    res = await self.update_cart_message(user_id, chat_id)
                    if res:
                        text, buttons = res
                        await event.edit(text, buttons=buttons)
                        
            except Exception as e:
                logger.error(f"Error in clear_cart: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def handle_product_action(self, event, user_id: int):
        """Handle product-related actions"""
        try:
            data = event.data.decode()
            if (data.startswith("edit_product_")):
                product_id = int(data.split('_')[2])
                await self.start_edit_product(event, product_id)
            elif (data.startswith("delete_product_")):
                product_id = int(data.split('_')[2])
                await self.delete_product(event, product_id)
            # Add other product action handlers as needed
        except Exception as e:
            logger.error(f"Error in handle_product_action: {e}")
            await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def show_categories(self, event):
        """Show available categories as buttons"""
        with SessionLocal() as db:
            categories = db.query(Category).all()
            if not categories:
                await event.respond(Messages.NO_CATEGORIES)
                # Clear state and show main menu
                user_id = event.sender_id
                if user_id in self.user_states:
                    del self.user_states[user_id]
                # Show main menu for seller
                with SessionLocal() as db:
                    seller = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if seller:
                        await event.respond(
                            Messages.WELCOME_BACK.format(
                                username=seller.username,
                                role=seller.role.lower()
                            ),
                            buttons=get_role_keyboard(seller.role.lower())
                        )
                return

            # Create buttons for each category
            buttons = []
            for category in categories:
                buttons.append([
                    Button.inline(
                        category.name,
                        f"select_category_{category.id}"
                    )
                ])
            
            # Add cancel button
            buttons.append([Button.inline("❌ Cancel", "cancel_product_add")])
            
            await event.respond(
                Messages.SELECT_CATEGORY,
                buttons=buttons
            )

    async def show_provinces(self, event):
        """Show provinces list for product location"""
        user_id = event.sender_id
        state = self.user_states.get(user_id)
        
        # Only show provinces if we're in product creation/editing
        if not state or state["action"] != "add_product":
            return
            
        with SessionLocal() as db:
            provinces = db.query(Province).all()
            buttons = []
            for province in provinces:
                buttons.append([
                    Button.inline(
                        province.name,
                        f"product_province_{province.id}"  # Changed callback data
                    )
                ])
            buttons.append([Button.inline("❌ Cancel", "cancel_product_add")])
            await event.respond(Messages.SELECT_PROVINCE, buttons=buttons)

    async def show_cities(self, event, province_id: int):
        """Show cities for product location"""
        with SessionLocal() as db:
            cities = db.query(City).filter(City.province_id == province_id).all()
            buttons = []
            for city in cities:
                buttons.append([
                    Button.inline(
                        city.name,
                        f"product_city_{city.id}"  # Changed callback data
                    )
                ])
            buttons.append([Button.inline("❌ Cancel", "cancel_product_add")])
            await event.respond(Messages.SELECT_CITY, buttons=buttons)

    async def get_product_stats(self, seller_id: int) -> str:
        """Get seller's products statistics"""
        with SessionLocal() as db:
            total_products = db.query(Product).filter(
                Product.seller_id == seller_id,
                Product.deleted_at.is_(None)
            ).count()
            
            active_products = db.query(Product).filter(
                Product.seller_id == seller_id,
                Product.status == 'active',
                Product.deleted_at.is_(None)
            ).count()
            
            total_stock = db.query(func.sum(Product.stock)).filter(
                Product.seller_id == seller_id,
                Product.deleted_at.is_(None)
            ).scalar() or 0

            out_of_stock = db.query(Product).filter(
                Product.seller_id == seller_id,
                Product.stock == 0,
                Product.deleted_at.is_(None)
            ).count()

            return Messages.PRODUCT_STATS.format(
                total=total_products,
                active=active_products,
                stock=total_stock,
                out_of_stock=out_of_stock
            )

    async def save_product(self, event, user_id: int, data: Dict):
        """Save product to database"""
        try:
            with SessionLocal() as db:
                seller = db.query(User).filter(User.telegram_id == str(user_id)).first()
                
                if "city_id" not in data:
                    await event.respond(Messages.NO_CITY_SELECTED)
                    return

                new_product = Product(
                    seller_id=seller.id,
                    name=data["name"],
                    description=data["description"],
                    price=data["price"],
                    stock=data["stock"],
                    weight=data["weight"],
                    category_id=data["category_id"],
                    city_id=data["city_id"],
                    zone=data["zone"],
                    status="active"
                )
                db.add(new_product)
                db.commit()

                # Clear user state
                del self.user_states[user_id]
                await event.respond(Messages.PRODUCT_ADDED)
                await self.show_products_list(event)

        except Exception as e:
            logger.error(f"Error saving product: {e}", exc_info=True)
            await event.respond(Messages.PRODUCT_SAVE_ERROR)
            if 'db' in locals():
                db.rollback()

    async def show_products_list(self, event):
        """Show products list based on user role"""
        try:
            user_id = event.sender_id
            with SessionLocal() as db:
                user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                if not user:
                    await event.answer(Messages.UNAUTHORIZED, alert=True)
                    return

                # Get user's cart items for quantity display
                cart_items = {item.product_id: item.quantity for item in db.query(CartItem).filter(
                    CartItem.user_id == user.id
                ).all()}

                # Get products based on role
                if user.role == "SELLER":
                    products = db.query(Product).filter(
                        Product.seller_id == user.id,
                        Product.deleted_at.is_(None)
                    ).all()
                    await self.show_seller_products(event, products)
                else:  # CUSTOMER or ADMIN view
                    products = db.query(Product).filter(
                        Product.status == 'active',
                        Product.deleted_at.is_(None)
                    ).all()

                    message = "🛍 Available Products:\n\n"
                    buttons = []
                    
                    for product in products:
                        current_qty = cart_items.get(product.id, 0)
                        # Display product name with price
                        buttons.append([
                            Button.inline(
                                f"{product.name} - {product.price}💰",
                                f"view_{product.id}"
                            )
                        ])
                        # Add + and - buttons in next row
                        buttons.append([
                            Button.inline("➖", f"decrease_{product.id}"),
                            Button.inline(f"🛒 {current_qty}", f"cart_{product.id}"),
                            Button.inline("➕", f"increase_{product.id}")
                        ])

                    # Add cart and main menu buttons
                    buttons.extend([
                        [Button.inline("🛒 View Cart", "view_cart")],
                        [Button.inline("🔙 Back to Main Menu", "back_to_main")]
                    ])

                    await event.edit(message, buttons=buttons)

        except Exception as e:
            logger.error(f"Error in show_products_list: {e}")
            await event.answer(Messages.ERROR_OCCURRED, alert=True)

    async def show_seller_products(self, event, products):
        """Show products with seller options"""
        for product in products:
            try:
                image = None
                with SessionLocal() as db:
                    product_image = db.query(ProductImage).filter(
                        ProductImage.product_id == product.id
                    ).first()
                    if product_image:
                        image = product_image.image_url

                # Create product details message
                message = Messages.SELLER_PRODUCT_DETAILS.format(
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    stock=product.stock,
                    category=product.category.name,
                    status=product.status
                )

                # Create product management buttons - removed back button
                buttons = [
                    [
                        Button.inline("📦 Change Stock", f"change_stock_{product.id}"),
                        Button.inline("❌ Delete", f"delete_product_{product.id}")
                    ]
                ]

                # Send product info with image and buttons
                if image:
                    await event.respond(
                        file=image,
                        message=message,
                        buttons=buttons
                    )
                else:
                    await event.respond(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error showing seller product {product.id}: {e}")
                continue

        # Add "Add Product" and "Back to Menu" buttons at the end
        await event.respond(
            Messages.ADD_PRODUCT_PROMPT,
            buttons=[
                [Button.inline("➕ Add New Product", "add_product")],
                [Button.inline("🔙 Back to Main Menu", "back_to_main")]
            ]
        )

    async def show_customer_products(self, event, products):
        """Show products with customer options"""
        for product in products:
            try:
                # Get product image
                image = None
                with SessionLocal() as db:
                    product_image = db.query(ProductImage).filter(
                        ProductImage.product_id == product.id
                    ).first()
                    if product_image:
                        image = product_image.image_url

                # Create product details message
                message = Messages.CUSTOMER_PRODUCT_DETAILS.format(
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    stock=product.stock,
                    category=product.category.name
                )

                # Create quantity selection buttons - removed back button
                buttons = [
                    [
                        Button.inline("➖", f"decrease_qty_{product.id}"),
                        Button.inline("0", f"qty_{product.id}"),
                        Button.inline("➕", f"increase_qty_{product.id}")
                    ],
                    [
                        Button.inline(f"💰 {product.price}", f"price_{product.id}"),
                        Button.inline("🛒 Add to Cart", f"add_cart_{product.id}")
                    ]
                ]

                # Send product info with image and buttons
                if image:
                    await event.respond(
                        file=image,
                        message=message,
                        buttons=buttons
                    )
                else:
                    await event.respond(message, buttons=buttons)

            except Exception as e:
                logger.error(f"Error showing customer product {product.id}: {e}")
                continue

        # Add "Back to Menu" button at the end
        await event.respond(
            "🔙 Return to main menu",
            buttons=[[Button.inline("🔙 Back to Main Menu", "back_to_main")]]
        )

    async def handle_product_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle product commands"""
        try:
            command = message.get('text', '').split()[0].lower()
            
            if command == '/products':
                await self.handle_list_products(message, context)
            elif command == '/product':
                await self.handle_product_details(message, context)
            elif command == '/add_to_cart':
                await self.handle_add_to_cart(message, context)
            elif command == '/remove_from_cart':
                await self.handle_remove_from_cart(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid product command. Available commands:\n"
                         "/products - List all products\n"
                         "/product <id> - View product details\n"
                         "/add_to_cart <id> <quantity> - Add product to cart\n"
                         "/remove_from_cart <id> - Remove product from cart"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing product command: {str(e)}"
            )

    async def handle_list_products(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /products command"""
        try:
            products = self.get_available_products()
            
            if not products:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="No products available at the moment."
                )
                return
            
            products_text = "🛍️ Available Products:\n\n"
            for product in products:
                products_text += (
                    f"ID: {product.id}\n"
                    f"Name: {product.name}\n"
                    f"Price: {product.price} USDT\n"
                    f"Stock: {product.stock}\n"
                    f"Category: {product.category}\n\n"
                )
            
            products_text += "Use /product <id> to view more details about a specific product."
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=products_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error listing products: {str(e)}"
            )

    async def handle_product_details(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /product command"""
        try:
            # Get product ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the product ID")
            
            product_id = int(parts[1])
            
            # Get product details
            product = self.get_product(product_id)
            if not product:
                raise ProductError("Product not found")
            
            details_text = (
                f"📦 Product Details:\n\n"
                f"Name: {product.name}\n"
                f"Price: {product.price} USDT\n"
                f"Stock: {product.stock}\n"
                f"Category: {product.category}\n"
                f"Description: {product.description}\n\n"
                f"Use /add_to_cart {product.id} <quantity> to add this product to your cart."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=details_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing product details: {str(e)}"
            )

    async def handle_add_to_cart(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /add_to_cart command"""
        try:
            # Get product ID and quantity from message
            parts = message.get('text', '').split()
            if len(parts) < 3:
                raise ValidationError("Please provide the product ID and quantity")
            
            product_id = int(parts[1])
            quantity = int(parts[2])
            
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than 0")
            
            # Add to cart
            user_id = message['from']['id']
            cart_data = {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity
            }
            
            cart_item = self.order_manager.add_to_cart(cart_data)
            
            confirm_text = (
                "✅ Added to Cart!\n\n"
                f"Product: {cart_item.product.name}\n"
                f"Quantity: {cart_item.quantity}\n"
                f"Price: {cart_item.price} USDT\n"
                f"Subtotal: {cart_item.quantity * cart_item.price} USDT\n\n"
                "Use /cart to view your cart or /checkout to complete your purchase."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=confirm_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error adding to cart: {str(e)}"
            )

    async def handle_remove_from_cart(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /remove_from_cart command"""
        try:
            # Get product ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the product ID")
            
            product_id = int(parts[1])
            
            # Remove from cart
            user_id = message['from']['id']
            self.order_manager.remove_from_cart(user_id, product_id)
            
            confirm_text = (
                "✅ Removed from Cart!\n\n"
                f"Product ID: {product_id} has been removed from your cart.\n"
                "Use /cart to view your updated cart."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=confirm_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error removing from cart: {str(e)}"
            )

    def get_available_products(self) -> List[Any]:
        """Get available products"""
        from src.core.models import Product
        return Product.get_available()

    def get_product(self, product_id: int) -> Any:
        """Get product by ID"""
        from src.core.models import Product
        return Product.get_by_id(product_id)
