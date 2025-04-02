from src.bot.common.keyboards import CartKeyboards  # Add this import

# ...existing code...

    async def show_cart(self, event):
        # ...existing code...
        buttons = CartKeyboards.get_cart_management()
        await event.edit(message, buttons=buttons)

    async def show_cart_item(self, event, item_id):
        # ...existing code...
        buttons = CartKeyboards.get_cart_item_options(item_id)
        await event.edit(message, buttons=buttons)
