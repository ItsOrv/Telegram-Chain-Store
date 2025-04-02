from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, UserRole
from src.bot.common.messages import Messages
from typing import Dict, Any
import logging
from src.core.exceptions import ValidationError
from src.core.services.support_manager import SupportManager

logger = logging.getLogger(__name__)

class SupportHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        self.setup_handlers()
        self.admin_id = None  # این مقدار باید در زمان راه‌اندازی بات تنظیم شود
        self.support_manager = SupportManager()

    def set_admin_id(self, admin_id):
        """Set the main admin's Telegram ID"""
        self.admin_id = admin_id

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="📞 Contact Support"))
        async def start_support_chat(event):
            """Start support conversation"""
            try:
                user_id = event.sender_id
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                # Set user state
                self.user_states[user_id] = {
                    "action": "support_chat",
                    "step": "waiting_message"
                }

                buttons = [[Button.inline("❌ Cancel", "cancel_support")]]
                await event.edit("🎯 شما به پشتیبانی متصل شدید.\n📝 لطفاً پیام خود را ارسال کنید.", buttons=buttons)

            except Exception as e:
                logger.error(f"Error in start_support_chat: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.CallbackQuery(pattern="cancel_support"))
        async def cancel_support(event):
            """Cancel support conversation"""
            try:
                user_id = event.sender_id
                if user_id in self.user_states:
                    del self.user_states[user_id]

                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if user:
                        from src.bot.common.keyboards import get_role_keyboard
                        await event.edit("✅ گفتگو با پشتیبانی لغو شد.", 
                                      buttons=get_role_keyboard(user.role.lower()))

            except Exception as e:
                logger.error(f"Error in cancel_support: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_support_message(event):
            """Handle messages in support conversation"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state or state["action"] != "support_chat":
                return

            try:
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if not user:
                        return

                    # ارسال پیام به ادمین
                    if self.admin_id:
                        user_message = event.message.text
                        admin_message = (
                            f"📨 پیام جدید از کاربر:\n"
                            f"👤 نام کاربری: {user.username or 'بدون نام'}\n"
                            f"🆔 شناسه: {user.telegram_id}\n"
                            f"📝 پیام:\n{user_message}"
                        )
                        
                        # ارسال به ادمین با دکمه پاسخ
                        buttons = [[Button.inline(f"📤 پاسخ به {user.username or 'کاربر'}", f"reply_{user.telegram_id}")]]
                        await self.client.send_message(self.admin_id, admin_message, buttons=buttons)
                        
                        # پیام تایید به کاربر و نمایش منوی اصلی
                        await event.respond("✅ پیام شما با موفقیت به پشتیبانی ارسال شد.")
                        from src.bot.common.keyboards import get_role_keyboard
                        await event.respond("🏠 به منوی اصلی بازگشتید:", 
                                         buttons=get_role_keyboard(user.role.lower()))
                        
                        # پاک کردن وضعیت کاربر
                        del self.user_states[user_id]

            except Exception as e:
                logger.error(f"Error in handle_support_message: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

        @self.client.on(events.CallbackQuery(pattern=r"reply_\d+"))
        async def start_admin_reply(event):
            """Start admin reply process"""
            try:
                if event.sender_id != self.admin_id:
                    await event.answer(Messages.UNAUTHORIZED, alert=True)
                    return

                user_telegram_id = event.data.decode().split('_')[1]
                self.user_states[self.admin_id] = {
                    "action": "admin_reply",
                    "user_telegram_id": user_telegram_id
                }

                await event.edit("📝 لطفاً پاسخ خود را بنویسید.")

            except Exception as e:
                logger.error(f"Error in start_admin_reply: {e}")
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @self.client.on(events.NewMessage())
        async def handle_admin_reply(event):
            """Handle admin's reply to user"""
            if event.sender_id != self.admin_id:
                return

            state = self.user_states.get(self.admin_id)
            if not state or state["action"] != "admin_reply":
                return

            try:
                user_telegram_id = state["user_telegram_id"]
                admin_reply = event.message.text

                # ارسال پاسخ به کاربر
                user_message = (
                    "📨 پاسخ از پشتیبانی:\n"
                    f"📝 {admin_reply}"
                )
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == user_telegram_id).first()
                    if user:
                        await self.client.send_message(int(user_telegram_id), user_message)
                        from src.bot.common.keyboards import get_role_keyboard
                        await self.client.send_message(int(user_telegram_id), 
                                                     "🏠 به منوی اصلی بازگشتید:", 
                                                     buttons=get_role_keyboard(user.role.lower()))

                # پاک کردن وضعیت ادمین
                del self.user_states[self.admin_id]
                
                # تایید ارسال به ادمین و نمایش منوی اصلی
                await event.respond("✅ پاسخ شما با موفقیت ارسال شد.")
                from src.bot.common.keyboards import get_role_keyboard
                await event.respond("🏠 به منوی اصلی بازگشتید:", 
                                 buttons=get_role_keyboard("admin"))

            except Exception as e:
                logger.error(f"Error in handle_admin_reply: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

    async def handle_support_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle support commands"""
        try:
            command = message.get('text', '').split()[0].lower()
            
            if command == '/support':
                await self.handle_support_menu(message, context)
            elif command == '/contact_support':
                await self.handle_contact_support(message, context)
            elif command == '/faq':
                await self.handle_faq(message, context)
            elif command == '/report_issue':
                await self.handle_report_issue(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid support command. Available commands:\n"
                         "/support - Show support menu\n"
                         "/contact_support - Contact support team\n"
                         "/faq - View frequently asked questions\n"
                         "/report_issue - Report an issue"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing support command: {str(e)}"
            )

    async def handle_support_menu(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /support command"""
        try:
            menu_text = (
                "💬 Support Menu:\n\n"
                "How can we help you today?\n\n"
                "1️⃣ /contact_support - Contact our support team\n"
                "2️⃣ /faq - View frequently asked questions\n"
                "3️⃣ /report_issue - Report an issue\n\n"
                "Support Hours: 24/7\n"
                "Response Time: Within 24 hours\n\n"
                "For urgent issues, please use /contact_support"
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=menu_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error showing support menu: {str(e)}"
            )

    async def handle_contact_support(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /contact_support command"""
        try:
            contact_text = (
                "📞 Contact Support:\n\n"
                "You can reach our support team through:\n\n"
                "1️⃣ Telegram: @support_bot\n"
                "2️⃣ Email: support@example.com\n"
                "3️⃣ Support Channel: @support_channel\n\n"
                "Support Hours: 24/7\n"
                "Response Time: Within 24 hours\n\n"
                "For urgent issues, please use our Telegram support channel."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=contact_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error showing contact information: {str(e)}"
            )

    async def handle_faq(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /faq command"""
        try:
            faqs = self.support_manager.get_faqs()
            
            faq_text = "❓ Frequently Asked Questions:\n\n"
            for faq in faqs:
                faq_text += (
                    f"Q: {faq.question}\n"
                    f"A: {faq.answer}\n\n"
                )
            
            faq_text += "Need more help? Use /contact_support to reach our support team."
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=faq_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error showing FAQs: {str(e)}"
            )

    async def handle_report_issue(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /report_issue command"""
        try:
            # Get issue description from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide a description of the issue")
            
            issue_description = ' '.join(parts[1:])
            user_id = message['from']['id']
            
            # Create support ticket
            ticket_data = {
                "user_id": user_id,
                "description": issue_description,
                "status": "open"
            }
            
            ticket = self.support_manager.create_ticket(ticket_data)
            
            confirm_text = (
                "✅ Issue Reported!\n\n"
                f"Ticket ID: #{ticket.id}\n"
                f"Status: {ticket.status}\n"
                f"Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "Our support team will review your issue and get back to you soon.\n"
                "Use /contact_support if you need immediate assistance."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=confirm_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error reporting issue: {str(e)}"
            )
