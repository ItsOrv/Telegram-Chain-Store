from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, Product, Category, City, Province, ProductImage
from src.bot.common.messages import Messages
from decimal import Decimal
from typing import Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductManagerHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()

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

            return Messages.PRODUCT_STATS.format(
                total=total_products,
                active=active_products,
                stock=total_stock
            )

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="🛍 Manage My Products"))
        async def show_products_management(event):
            """Show seller's products management panel"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    seller = db.query(User).filter(User.telegram_id == user_id).first()
                    if not seller or seller.role != "SELLER":
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                    # Get products statistics
                    stats = await self.get_product_stats(seller.id)
                    
                    # Get all products for this seller
                    products = db.query(Product).filter(
                        Product.seller_id == seller.id,
                        Product.deleted_at.is_(None)
                    ).all()
                    
                    # Create buttons for each product
                    buttons = [
                        [Button.inline(
                            f"{product.name} ({product.stock} in stock)",
                            f"product_{product.id}"
                        )] for product in products
                    ]
                    
                    # Add "Add Product" button
                    buttons.append([Button.inline("➕ Add New Product", "add_product")])
                    buttons.append([Button.inline("🔙 Back to Main Menu", "back_to_main")])

                    await event.edit(stats, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in show_products_management: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_product"))
        async def start_add_product(event):
            """Start product creation process"""
            try:
                user_id = event.sender_id
                self.user_states[user_id] = {
                    "action": "add_product",
                    "step": "name",
                    "data": {}
                }
                await event.edit(Messages.ADD_PRODUCT_NAME)
            except Exception as e:
                logger.error(f"Error in start_add_product: {e}")
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

                if step == "name":
                    data["name"] = event.text
                    state["step"] = "description"
                    await event.respond(Messages.ADD_PRODUCT_DESCRIPTION)

                elif step == "description":
                    data["description"] = event.text
                    state["step"] = "price"
                    await event.respond(Messages.ADD_PRODUCT_PRICE)

                elif step == "price":
                    try:
                        data["price"] = Decimal(event.text)
                        state["step"] = "stock"
                        await event.respond(Messages.ADD_PRODUCT_STOCK)
                    except:
                        await event.respond(Messages.INVALID_PRICE)
                        return

                elif step == "stock":
                    try:
                        data["stock"] = int(event.text)
                        state["step"] = "min_order"
                        await event.respond(Messages.ADD_PRODUCT_MIN_ORDER)
                    except:
                        await event.respond(Messages.INVALID_NUMBER)
                        return

                elif step == "min_order":
                    try:
                        data["min_order"] = int(event.text)
                        state["step"] = "max_order"
                        await event.respond(Messages.ADD_PRODUCT_MAX_ORDER)
                    except:
                        await event.respond(Messages.INVALID_NUMBER)
                        return

                elif step == "max_order":
                    try:
                        if event.text.lower() != "none":
                            data["max_order"] = int(event.text)
                        state["step"] = "weight"
                        await event.respond(Messages.ADD_PRODUCT_WEIGHT)
                    except:
                        await event.respond(Messages.INVALID_NUMBER)
                        return

                elif step == "weight":
                    try:
                        data["weight"] = Decimal(event.text)
                        state["step"] = "category"
                        # Show categories as buttons
                        await self.show_categories(event)
                    except:
                        await event.respond(Messages.INVALID_NUMBER)
                        return

                elif step == "province":
                    # Show cities of selected province
                    await self.show_cities(event, data["province_id"])
                    state["step"] = "city"

                elif step == "zone":
                    data["zone"] = event.text
                    state["step"] = "image"
                    await event.respond(Messages.ADD_PRODUCT_IMAGE)

                elif step == "image":
                    if event.photo:
                        data["image"] = await event.download_media()
                        # Save product to database
                        await self.save_product(event, user_id, data)
                    else:
                        await event.respond(Messages.INVALID_IMAGE)

            except Exception as e:
                logger.error(f"Error handling product input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

    async def save_product(self, event, user_id: int, data: Dict):
        """Save product to database"""
        try:
            with SessionLocal() as db:
                seller = db.query(User).filter(User.telegram_id == user_id).first()
                
                new_product = Product(
                    seller_id=seller.id,
                    name=data["name"],
                    description=data["description"],
                    price=data["price"],
                    stock=data["stock"],
                    min_order=data["min_order"],
                    max_order=data.get("max_order"),
                    weight=data["weight"],
                    category_id=data["category_id"],
                    city_id=data["city_id"],
                    zone=data["zone"],
                    status="active"
                )
                db.add(new_product)
                db.commit()

                # Save product image
                if "image" in data:
                    product_image = ProductImage(
                        product_id=new_product.id,
                        image_url=data["image"]
                    )
                    db.add(product_image)
                    db.commit()

                # Clear user state
                del self.user_states[user_id]
                
                await event.respond(Messages.PRODUCT_ADDED)
                await show_products_management(event)

        except Exception as e:
            logger.error(f"Error saving product: {e}")
            await event.respond(Messages.PRODUCT_SAVE_ERROR)
