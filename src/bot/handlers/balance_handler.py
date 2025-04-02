from src.bot.common.keyboards import BalanceKeyboards, DialogKeyboards
from src.bot.common.messages import Messages

class BalanceHandler:
    def __init__(self, client):
        self.client = client
        self.setup_handlers()

    async def show_charge_options(self, event):
        """Show balance charge options"""
        buttons = BalanceKeyboards.get_charge_options()
        await event.edit(Messages.CHARGE_OPTIONS, buttons=buttons)

    async def show_charge_amounts(self, event):
        """Show charge amount options"""
        buttons = BalanceKeyboards.get_charge_amounts()
        await event.edit(Messages.SELECT_AMOUNT, buttons=buttons)

    # ...rest of the code...
