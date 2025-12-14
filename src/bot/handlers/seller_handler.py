from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, UserRole, Product, Order
from src.bot.common.messages import Messages
from src.bot.common.keyboards import AdminKeyboards, RoleKeyboard, BaseKeyboard
from typing import Dict
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

class SellerHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()

    async def get_sellers_stats(self) -> str:
        """Get sellers statistics"""
        with SessionLocal() as db:
            total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()
            active_sellers = db.query(User).filter(
                User.role == UserRole.SELLER,
                User.status == "ACTIVE"
            ).count()
            
            # Get total products and orders
            total_products = db.query(Product).join(User).filter(User.role == UserRole.SELLER).count()
            total_orders = db.query(Order).join(Product).join(User).filter(User.role == UserRole.SELLER).count()

            return Messages.SELLERS_STATS.format(
                total=total_sellers,
                active=active_sellers,
                products=total_products,
                orders=total_orders
            )

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="👥 Manage Sellers"))
        async def show_sellers_management(event):
            """Show sellers management panel"""
            try:
                # Check if user is admin
                user_id = event.sender_id
                with SessionLocal() as db:
                    admin = db.query(User).filter(User.telegram_id == user_id).first()
                    if admin.role != UserRole.ADMIN:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                    # Get sellers statistics
                    stats = await self.get_sellers_stats()
                    
                    # Get all sellers
                    sellers = db.query(User).filter(User.role == UserRole.SELLER).all()
                    buttons = AdminKeyboards.get_sellers_management(sellers)
                    await event.edit(stats, buttons=buttons)

            except Exception as e:
                logger.error(f"Error in show_sellers_management: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"seller_\d+"))
        async def seller_options(event):
            """Show options for selected seller"""
            try:
                seller_id = int(event.data.decode().split('_')[1])
                buttons = AdminKeyboards.get_seller_options(seller_id)
                
                with SessionLocal() as db:
                    seller = db.query(User).filter(User.id == seller_id).first()
                    if not seller:
                        await event.answer(Messages.USER_NOT_FOUND, alert=True)
                        return
                        
                    # Get seller's stats
                    products_count = db.query(Product).filter(Product.seller_id == seller_id).count()
                    orders_count = db.query(Order).join(Product).filter(Product.seller_id == seller_id).count()
                    
                    message = Messages.SELLER_DETAILS.format(
                        username=seller.username or f"Seller_{seller.telegram_id}",
                        products=products_count,
                        orders=orders_count,
                        status=seller.status
                    )
                    
                    await event.edit(message, buttons=buttons)
                    
            except Exception as e:
                logger.error(f"Error in seller_options: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_seller"))
        async def start_add_seller(event):
            """Start seller creation process"""
            try:
                user_id = event.sender_id
                self.user_states[user_id] = {"action": "add_seller"}
                await event.edit(Messages.ENTER_SELLER_ID)
            except Exception as e:
                logger.error(f"Error in start_add_seller: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"delete_seller_\d+"))
        async def delete_seller(event):
            """Delete seller"""
            try:
                seller_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    seller = db.query(User).filter(User.id == seller_id).first()
                    if not seller:
                        await event.answer(Messages.USER_NOT_FOUND, alert=True)
                        return
                        
                    # Change role to CUSTOMER instead of deleting
                    seller.role = UserRole.CUSTOMER
                    db.commit()
                    
                    await event.answer(Messages.SELLER_DELETED, alert=True)
                    # Show updated sellers list
                    await show_sellers_management(event)
                    
            except Exception as e:
                logger.error(f"Error in delete_seller: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_sellers"))
        async def handle_back_to_sellers(event):
            """Handle back to sellers list button"""
            try:
                # Simply call the show_sellers_management function
                await show_sellers_management(event)
            except Exception as e:
                logger.error(f"Error in handle_back_to_sellers: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_seller_input(event):
            """Handle seller ID input for adding new seller"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state or state["action"] != "add_seller":
                return

            try:
                new_seller_id = str(int(event.text))  # Validate numeric ID
                
                with SessionLocal() as db:
                    # Check if user exists and is not already a seller
                    user = db.query(User).filter(User.telegram_id == new_seller_id).first()
                    if not user:
                        await event.respond(Messages.USER_NOT_FOUND)
                        return
                    
                    if user.role == UserRole.SELLER:
                        await event.respond(Messages.ALREADY_SELLER)
                        return
                    
                    # Update user role to seller
                    user.role = UserRole.SELLER
                    db.commit()
                    
                    # Clear state and send confirmation
                    del self.user_states[user_id]
                    await event.respond(Messages.SELLER_ADDED)
                    
                    # Show updated sellers list
                    stats = await self.get_sellers_stats()
                    sellers = db.query(User).filter(User.role == UserRole.SELLER).all()
                    buttons = [
                        [Button.inline(
                            f"👤 {seller.username or f'Seller_{seller.telegram_id}'}",
                            f"seller_{seller.id}"
                        )] for seller in sellers
                    ]
                    buttons.append([Button.inline("➕ Add New Seller", "add_seller")])
                    buttons.append([Button.inline("🔙 Back to Main Menu", "back_to_main")])
                    
                    await event.respond(stats, buttons=buttons)

            except ValueError:
                await event.respond(Messages.INVALID_USER_ID)
            except Exception as e:
                logger.error(f"Error handling seller input: {e}")
                await event.respond(Messages.ERROR_OCCURRED)
