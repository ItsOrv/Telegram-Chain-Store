from telethon import events, Button
from decimal import Decimal
from typing import Dict, Any

from src.bot.common.messages import Messages
from src.core.models import Product, Category, City, ProductImage
from src.core.database import SessionLocal
from src.bot.common.keyboards import (
    DialogKeyboards,
    BackKeyboards
)

class ProductDialog:
    """Handle product creation dialog"""
    def __init__(self):
        self.user_states = {}
        self.product_data = {}

    async def start_dialog(self, event):
        user_id = event.sender_id
        self.user_states[user_id] = "awaiting_name"
        self.product_data[user_id] = {}
        await event.respond(Messages.ADD_PRODUCT_NAME)

    async def handle_response(self, event):
        user_id = event.sender_id
        state = self.user_states.get(user_id)
        
        if not state:
            return
            
        if state == "awaiting_name":
            self.product_data[user_id]['name'] = event.text
            self.user_states[user_id] = "awaiting_price"
            await event.respond(Messages.ADD_PRODUCT_PRICE)
            
        elif state == "awaiting_price":
            try:
                price = Decimal(event.text)
                self.product_data[user_id]['price'] = price
                self.user_states[user_id] = "awaiting_description"
                await event.respond(Messages.ADD_PRODUCT_DESCRIPTION)
            except:
                await event.respond(Messages.INVALID_PRICE)
                
        # Continue with other dialog states...
