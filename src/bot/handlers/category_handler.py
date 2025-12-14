from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import Category, Product, User, UserRole
from src.bot.common.messages import Messages
from src.bot.common.keyboards import get_role_keyboard  # Add this import
from src.bot.common.keyboards import CategoryKeyboards  # Add this import
from sqlalchemy import update
from typing import List
import logging
import traceback
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger('category_handler')
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(
    log_dir / f"category_handler_{datetime.now().strftime('%Y-%m-%d')}.log"
)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(levelname)s - %(message)s')
)
logger.addHandler(console_handler)

class CategoryHandler:
    def __init__(self, client):
        self.client = client
        self.user_states = {}  # Store user states for dialog
        self.setup_handlers()

    async def show_categories(self, event, edit=True):
        """Show list of categories"""
        try:
            logger.info(f"Showing categories list for user {event.sender_id}")
            user_id = event.sender_id
            
            with SessionLocal() as db:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if user.role != UserRole.ADMIN:
                    if hasattr(event, 'answer'):
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                    else:
                        await event.respond(Messages.UNAUTHORIZED)
                    return

                # Get all categories
                categories = db.query(Category).all()
                
                # Create buttons for each category
                buttons = CategoryKeyboards.get_categories_list(categories)
                
                if edit and hasattr(event, 'edit'):
                    await event.edit(Messages.CATEGORY_LIST, buttons=buttons)
                else:
                    await event.respond(Messages.CATEGORY_LIST, buttons=buttons)

        except Exception as e:
            logger.error(f"Error in show_categories: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            if hasattr(event, 'answer'):
                await event.answer(Messages.ERROR_OCCURRED, alert=True)
            else:
                await event.respond(Messages.ERROR_OCCURRED)

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="📁 Manage Categories"))
        async def show_categories(event):
            await self.show_categories(event)

        @self.client.on(events.CallbackQuery(pattern=r"cat_\d+"))
        async def category_options(event):
            """Show options for selected category"""
            try:
                category_id = int(event.data.decode().split('_')[1])
                
                buttons = CategoryKeyboards.get_category_options(category_id)
                
                with SessionLocal() as db:
                    category = db.query(Category).filter(Category.id == category_id).first()
                    await event.edit(
                        Messages.CATEGORY_OPTIONS.format(name=category.name),
                        buttons=buttons
                    )
            except Exception as e:
                logger.error(f"Error in category_options: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"del_cat_\d+"))
        async def delete_category(event):
            """Delete selected category"""
            try:
                category_id = int(event.data.decode().split('_')[2])
                
                with SessionLocal() as db:
                    try:
                        # Update products to remove category reference
                        db.execute(
                            update(Product)
                            .where(Product.category_id == category_id)
                            .values(category_id=None)
                        )
                        
                        # Delete category
                        db.query(Category).filter(Category.id == category_id).delete()
                        db.commit()
                        
                        await event.answer(Messages.CATEGORY_DELETED, alert=True)
                        # Show updated category list
                        await self.show_categories(event)
                        
                    except Exception as e:
                        db.rollback()
                        await event.answer(Messages.ERROR_OCCURRED, alert=True)
            except Exception as e:
                logger.error(f"Error in delete_category: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern=r"edit_cat_\d+"))
        async def start_edit_category(event):
            """Start category edit process"""
            try:
                category_id = int(event.data.decode().split('_')[2])
                user_id = event.sender_id
                
                # Set user state for editing
                self.user_states[user_id] = {
                    "action": "edit_category",
                    "category_id": category_id
                }
                
                await event.edit(Messages.ENTER_NEW_CATEGORY_NAME)
            except Exception as e:
                logger.error(f"Error in start_edit_category: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="add_category"))
        async def start_add_category(event):
            """Start category creation process"""
            try:
                user_id = event.sender_id
                logger.info(f"Starting category creation for user {user_id}")
                
                # Set user state for adding
                self.user_states[user_id] = {"action": "add_category"}
                logger.debug(f"Set user state: {self.user_states[user_id]}")
                
                await event.edit(Messages.ENTER_CATEGORY_NAME)
            except Exception as e:
                logger.error(f"Error in start_add_category: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_main"))
        async def handle_back_to_main(event):
            """Handle back to main menu button"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_id).first()
                    if user:
                        await event.edit(
                            Messages.WELCOME_BACK.format(
                                username=user.username,
                                role=user.role.lower()
                            ),
                            buttons=get_role_keyboard(user.role.lower())
                        )
            except Exception as e:
                logger.error(f"Error in handle_back_to_main: {str(e)}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="back_to_categories"))
        async def handle_back_to_categories(event):
            """Handle back to categories button"""
            try:
                await self.show_categories(event)
            except Exception as e:
                logger.error(f"Error in handle_back_to_categories: {str(e)}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_category_input(event):
            """Handle category name input"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state:
                return
                
            logger.info(f"Handling category input from user {user_id}")
            logger.debug(f"User state: {state}")
            logger.debug(f"Input text: {event.text}")
            
            with SessionLocal() as db:
                try:
                    if state["action"] == "add_category":
                        logger.info(f"Adding new category: {event.text}")
                        # Create new category
                        new_category = Category(
                            name=event.text,
                            slug=event.text.lower().replace(" ", "-")
                        )
                        db.add(new_category)
                        db.commit()
                        
                        logger.info(f"Category added successfully: {new_category.id}")
                        await event.respond(Messages.CATEGORY_ADDED)
                        
                    elif state["action"] == "edit_category":
                        logger.info(f"Editing category {state['category_id']} to: {event.text}")
                        # Update existing category
                        category = db.query(Category).filter(
                            Category.id == state["category_id"]
                        ).first()
                        
                        if not category:
                            logger.error(f"Category {state['category_id']} not found")
                            raise ValueError("Category not found")
                            
                        category.name = event.text
                        category.slug = event.text.lower().replace(" ", "-")
                        db.commit()
                        
                        logger.info("Category updated successfully")
                        await event.respond(Messages.CATEGORY_UPDATED)
                    
                    # Clear user state
                    del self.user_states[user_id]
                    
                    # Show updated category list
                    await self.show_categories(event, edit=False)
                    
                except Exception as e:
                    logger.error(f"Error in handle_category_input: {str(e)}")
                    logger.error(f"Traceback:\n{traceback.format_exc()}")
                    db.rollback()
                    await event.respond(
                        f"{Messages.ERROR_OCCURRED}\nError details: {str(e)}"
                    )
