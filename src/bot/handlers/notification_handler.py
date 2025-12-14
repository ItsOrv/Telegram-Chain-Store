from src.bot.common.keyboards import NotificationKeyboards, DialogKeyboards
from src.bot.common.messages import Messages
from src.core.database import SessionLocal
from src.core.models import User, Notification

class NotificationHandler:
    def __init__(self, client):
        self.client = client
        self.setup_handlers()

    async def show_notification_list(self, event):
        """Show user notifications"""
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == event.sender_id).first()
            notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
            buttons = NotificationKeyboards.get_notifications_list(notifications)
            await event.edit(Messages.NOTIFICATIONS_LIST, buttons=buttons)

    async def show_notification_options(self, event):
        """Show notification management options"""
        buttons = NotificationKeyboards.get_notification_options()
        await event.edit(Messages.NOTIFICATION_OPTIONS, buttons=buttons)

    async def show_notifications(self, event):
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == event.sender_id).first()
            notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
            buttons = NotificationKeyboards.get_notifications_list(notifications)
            await event.edit(Messages.NOTIFICATIONS_LIST, buttons=buttons)

    async def show_notification(self, event, notif_id):
        with SessionLocal() as db:
            notification = db.query(Notification).filter(Notification.id == notif_id).first()
            if not notification:
                await event.answer(Messages.NOTIFICATION_NOT_FOUND, alert=True)
                return
            buttons = NotificationKeyboards.get_notification_options()
            await event.edit(notification.message, buttons=buttons)
