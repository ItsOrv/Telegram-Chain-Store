from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.payment_service import PaymentService
from src.core.services.user_service import UserService
from src.core.services.order_service import OrderService
from src.bot.handlers.callback_router import register_callback
from typing import List, Dict, Any
from src.core.models.payment import PaymentStatus

# Initialize logger
logger = setup_logger("pending_payments_handler")

def register_pending_payments_callbacks():
    """Register pending payments callback handlers"""
    logger.info("Registering pending payments callbacks")
    
    @register_callback("admin:payments")
    async def handle_admin_payments(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle admin payment management callbacks"""
        try:
            if not params:
                # Show main payment management menu
                from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                await event.edit("💳 **مدیریت پرداخت‌ها**\n\nاز این بخش می‌توانید پرداخت‌های سیستم را مدیریت کنید.", 
                               buttons=get_admin_payments_keyboard())
                return
            
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("لطفا ابتدا ربات را استارت کنید", alert=True)
                    return
                
                # Check if user is admin
                if not user.is_admin:
                    await event.answer("شما مجوز دسترسی به پنل مدیریت را ندارید", alert=True)
                    return
                
                action = params[0]  # pending, approved, rejected, etc.
                payment_service = PaymentService(session)
                
                if action == "pending":
                    # Handle pending payments
                    page = int(params[1]) if len(params) > 1 else 1
                    await handle_pending_payments(event, page, payment_service, user_service)
                
                elif action == "approved":
                    # Handle approved payments
                    page = int(params[1]) if len(params) > 1 else 1
                    await handle_approved_payments(event, page, payment_service, user_service)
                
                elif action == "rejected":
                    # Handle rejected payments
                    page = int(params[1]) if len(params) > 1 else 1
                    await handle_rejected_payments(event, page, payment_service, user_service)
                
                elif action == "view":
                    # View payment details
                    if len(params) > 1:
                        payment_id = int(params[1])
                        await handle_view_payment(event, payment_id, payment_service, user_service)
                    else:
                        await event.answer("شناسه پرداخت نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                        await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                
                elif action == "approve":
                    # Approve payment
                    if len(params) > 1:
                        payment_id = int(params[1])
                        
                        if len(params) > 2 and params[2] == "confirm":
                            # Confirm approval
                            payment = payment_service.get_by_id(payment_id)
                            if payment:
                                payment_service.admin_verify_payment(payment_id, user.id)
                                await event.answer("پرداخت با موفقیت تأیید شد")
                                
                                # Update order status if there's an order attached
                                if payment.order_id:
                                    order_service = OrderService(session)
                                    order_service.update_order_status(payment.order_id, "processing")
                                
                                # Return to pending payments list
                                await handle_pending_payments(event, 1, payment_service, user_service)
                            else:
                                await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                                await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                        else:
                            # Ask for confirmation
                            payment = payment_service.get_by_id(payment_id)
                            if payment:
                                user_info = user_service.get_by_id(payment.user_id)
                                user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
                                
                                message = (
                                    f"✅ **تأیید پرداخت**\n\n"
                                    f"آیا از تأیید این پرداخت اطمینان دارید؟\n\n"
                                    f"🆔 شناسه پرداخت: {payment.id}\n"
                                    f"👤 کاربر: {user_name}\n"
                                    f"💰 مبلغ: {payment.amount} تومان\n"
                                    f"🕒 تاریخ: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                                )
                                
                                from src.bot.keyboards.admin_keyboard import PendingPaymentsKeyboards
                                keyboard = PendingPaymentsKeyboards.get_payment_confirmation(payment_id, "approve")
                                
                                await event.edit(message, buttons=keyboard)
                            else:
                                await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                                await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                    else:
                        await event.answer("شناسه پرداخت نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                        await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                
                elif action == "reject":
                    # Reject payment
                    if len(params) > 1:
                        payment_id = int(params[1])
                        
                        if len(params) > 2 and params[2] == "confirm":
                            # Confirm rejection
                            payment = payment_service.get_by_id(payment_id)
                            if payment:
                                payment_service.admin_reject_payment(payment_id, user.id)
                                await event.answer("پرداخت با موفقیت رد شد")
                                
                                # Update order status if there's an order attached
                                if payment.order_id:
                                    order_service = OrderService(session)
                                    order_service.update_order_status(payment.order_id, "payment_failed")
                                
                                # Return to pending payments list
                                await handle_pending_payments(event, 1, payment_service, user_service)
                            else:
                                await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                                await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                        else:
                            # Ask for confirmation
                            payment = payment_service.get_by_id(payment_id)
                            if payment:
                                user_info = user_service.get_by_id(payment.user_id)
                                user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
                                
                                message = (
                                    f"❌ **رد پرداخت**\n\n"
                                    f"آیا از رد این پرداخت اطمینان دارید؟\n\n"
                                    f"🆔 شناسه پرداخت: {payment.id}\n"
                                    f"👤 کاربر: {user_name}\n"
                                    f"💰 مبلغ: {payment.amount} تومان\n"
                                    f"🕒 تاریخ: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                                )
                                
                                from src.bot.keyboards.admin_keyboard import PendingPaymentsKeyboards
                                keyboard = PendingPaymentsKeyboards.get_payment_confirmation(payment_id, "reject")
                                
                                await event.edit(message, buttons=keyboard)
                            else:
                                await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                                await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                    else:
                        await event.answer("شناسه پرداخت نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                        await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                
                elif action == "details":
                    # Show payment details
                    if len(params) > 1:
                        payment_id = int(params[1])
                        await handle_payment_details(event, payment_id, payment_service, user_service, session)
                    else:
                        await event.answer("شناسه پرداخت نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                        await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                
                elif action == "note":
                    # Add note to payment
                    if len(params) > 1:
                        payment_id = int(params[1])
                        await handle_add_payment_note(event, payment_id, payment_service, user_service)
                    else:
                        await event.answer("شناسه پرداخت نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                        await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
                
                elif action == "back":
                    # Back to admin panel
                    from src.bot.keyboards.admin_keyboard import AdminKeyboards
                    keyboard = AdminKeyboards.get_admin_main_menu()
                    
                    message = (
                        "🛠️ **پنل مدیریت**\n\n"
                        f"خوش آمدید به پنل مدیریت، {user.first_name}.\n"
                        "از اینجا می‌توانید سیستم را مدیریت کنید.\n\n"
                        "لطفاً یک گزینه را انتخاب کنید:"
                    )
                    
                    await event.edit(message, buttons=keyboard)
                
                else:
                    await event.answer("عملیات نامعتبر", alert=True)
                    from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
                    await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
        
        except Exception as e:
            log_error("Error in handle_admin_payments", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_pending_payments(event: events.CallbackQuery.Event, page: int, payment_service: PaymentService, user_service: UserService) -> None:
    """Handle pending payments listing"""
    try:
        # Get pending payments with pagination
        per_page = 5
        pending_payments = payment_service.get_payments_by_status(PaymentStatus.PENDING, page=page, per_page=per_page)
        total_pending = payment_service.count_payments_by_status(PaymentStatus.PENDING)
        total_pages = (total_pending + per_page - 1) // per_page if total_pending > 0 else 1
        
        message = f"🔄 **پرداخت‌های در انتظار تأیید**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not pending_payments:
            message += "هیچ پرداخت در انتظار تأییدی وجود ندارد."
        else:
            for payment in pending_payments:
                user_info = user_service.get_by_id(payment.user_id)
                user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
                
                message += (
                    f"💰 پرداخت #{payment.id} - مبلغ: {payment.amount} تومان\n"
                    f"👤 کاربر: {user_name} (شناسه: {payment.user_id})\n"
                    f"🕒 تاریخ: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
        
        # Create keyboard with pending payments list
        from src.bot.keyboards.admin_keyboard import PendingPaymentsKeyboards
        keyboard = PendingPaymentsKeyboards.get_pending_payments_list(pending_payments, page, total_pages)
        
        await event.edit(message, buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_pending_payments", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_approved_payments(event: events.CallbackQuery.Event, page: int, payment_service: PaymentService, user_service: UserService) -> None:
    """Handle approved payments listing"""
    try:
        # Get approved payments with pagination
        per_page = 5
        approved_payments = payment_service.get_payments_by_status(PaymentStatus.APPROVED, page=page, per_page=per_page)
        total_approved = payment_service.count_payments_by_status(PaymentStatus.APPROVED)
        total_pages = (total_approved + per_page - 1) // per_page if total_approved > 0 else 1
        
        message = f"✅ **پرداخت‌های تأیید شده**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not approved_payments:
            message += "هیچ پرداخت تأیید شده‌ای وجود ندارد."
        else:
            for payment in approved_payments:
                user_info = user_service.get_by_id(payment.user_id)
                user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
                
                approved_by = "نامشخص"
                if payment.admin_verified_by:
                    admin_info = user_service.get_by_id(payment.admin_verified_by)
                    approved_by = f"{admin_info.first_name} {admin_info.last_name or ''}" if admin_info else "نامشخص"
                
                message += (
                    f"💰 پرداخت #{payment.id} - مبلغ: {payment.amount} تومان\n"
                    f"👤 کاربر: {user_name}\n"
                    f"✅ تأیید توسط: {approved_by}\n"
                    f"🕒 تاریخ تأیید: {payment.admin_verified_at.strftime('%Y-%m-%d %H:%M') if payment.admin_verified_at else 'نامشخص'}\n\n"
                )
        
        # Create keyboard with pagination
        buttons = []
        
        # Pagination buttons
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:payments:approved:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:payments:approved:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # Filter and option buttons
        buttons.append([
            Button.inline("🔍 جستجو", "admin:payments:search:approved"),
            Button.inline("📅 فیلتر تاریخ", "admin:payments:filter_date:approved")
        ])
        
        # Back button
        buttons.append([Button.inline("« بازگشت", "admin:payments")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_approved_payments", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_rejected_payments(event: events.CallbackQuery.Event, page: int, payment_service: PaymentService, user_service: UserService) -> None:
    """Handle rejected payments listing"""
    try:
        # Get rejected payments with pagination
        per_page = 5
        rejected_payments = payment_service.get_payments_by_status(PaymentStatus.REJECTED, page=page, per_page=per_page)
        total_rejected = payment_service.count_payments_by_status(PaymentStatus.REJECTED)
        total_pages = (total_rejected + per_page - 1) // per_page if total_rejected > 0 else 1
        
        message = f"❌ **پرداخت‌های رد شده**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not rejected_payments:
            message += "هیچ پرداخت رد شده‌ای وجود ندارد."
        else:
            for payment in rejected_payments:
                user_info = user_service.get_by_id(payment.user_id)
                user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
                
                rejected_by = "نامشخص"
                if payment.admin_rejected_by:
                    admin_info = user_service.get_by_id(payment.admin_rejected_by)
                    rejected_by = f"{admin_info.first_name} {admin_info.last_name or ''}" if admin_info else "نامشخص"
                
                message += (
                    f"💰 پرداخت #{payment.id} - مبلغ: {payment.amount} تومان\n"
                    f"👤 کاربر: {user_name}\n"
                    f"❌ رد توسط: {rejected_by}\n"
                    f"🕒 تاریخ رد: {payment.admin_rejected_at.strftime('%Y-%m-%d %H:%M') if payment.admin_rejected_at else 'نامشخص'}\n"
                    f"📝 دلیل: {payment.rejection_reason or 'دلیلی ذکر نشده است'}\n\n"
                )
        
        # Create keyboard with pagination
        buttons = []
        
        # Pagination buttons
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:payments:rejected:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:payments:rejected:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # Filter and option buttons
        buttons.append([
            Button.inline("🔍 جستجو", "admin:payments:search:rejected"),
            Button.inline("📅 فیلتر تاریخ", "admin:payments:filter_date:rejected")
        ])
        
        # Back button
        buttons.append([Button.inline("« بازگشت", "admin:payments")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_rejected_payments", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_view_payment(event: events.CallbackQuery.Event, payment_id: int, payment_service: PaymentService, user_service: UserService) -> None:
    """Handle viewing a payment"""
    try:
        payment = payment_service.get_by_id(payment_id)
        
        if not payment:
            await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
            from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
            await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
            return
        
        user_info = user_service.get_by_id(payment.user_id)
        user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
        
        status_text = {
            PaymentStatus.PENDING: "در انتظار تأیید",
            PaymentStatus.APPROVED: "تأیید شده",
            PaymentStatus.REJECTED: "رد شده",
            PaymentStatus.FAILED: "ناموفق",
            PaymentStatus.EXPIRED: "منقضی شده"
        }.get(payment.status, "نامشخص")
        
        # Get verifier info if available
        cardholder_verified_by = "نشده"
        admin_verified_by = "نشده"
        
        if payment.cardholder_verified_by:
            ch_info = user_service.get_by_id(payment.cardholder_verified_by)
            cardholder_verified_by = f"{ch_info.first_name} {ch_info.last_name or ''}" if ch_info else "نامشخص"
            cardholder_verified_by += f" ({payment.cardholder_verified_at.strftime('%Y-%m-%d %H:%M')})" if payment.cardholder_verified_at else ""
        
        if payment.admin_verified_by:
            admin_info = user_service.get_by_id(payment.admin_verified_by)
            admin_verified_by = f"{admin_info.first_name} {admin_info.last_name or ''}" if admin_info else "نامشخص"
            admin_verified_by += f" ({payment.admin_verified_at.strftime('%Y-%m-%d %H:%M')})" if payment.admin_verified_at else ""
        
        message = (
            f"💳 **جزئیات پرداخت #{payment.id}**\n\n"
            f"💰 مبلغ: {payment.amount} تومان\n"
            f"📊 وضعیت: {status_text}\n"
            f"🛒 سفارش مرتبط: {payment.order_id if payment.order_id else 'ندارد'}\n\n"
            f"👤 کاربر: {user_name} (شناسه: {payment.user_id})\n"
            f"💭 روش پرداخت: {payment.payment_method}\n"
            f"🆔 شناسه تراکنش: {payment.transaction_id or 'ندارد'}\n\n"
            f"✅ تأیید کارت‌دار: {cardholder_verified_by}\n"
            f"✅ تأیید ادمین: {admin_verified_by}\n\n"
            f"📝 توضیحات: {payment.description or 'ندارد'}\n"
            f"📅 تاریخ ایجاد: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        )
        
        # Create keyboard based on payment status
        buttons = []
        
        if payment.status == PaymentStatus.PENDING:
            # Action buttons for pending payments
            buttons.append([
                Button.inline("✅ تأیید پرداخت", f"admin:payments:approve:{payment_id}"),
                Button.inline("❌ رد پرداخت", f"admin:payments:reject:{payment_id}")
            ])
        
        # Add note button
        buttons.append([Button.inline("📝 افزودن یادداشت", f"admin:payments:note:{payment_id}")])
        
        # Receipt view button if available
        if payment.receipt_file_id:
            buttons.append([Button.inline("🖼️ مشاهده رسید", f"admin:payments:receipt:{payment_id}")])
        
        # Back buttons
        if payment.status == PaymentStatus.PENDING:
            buttons.append([Button.inline("« بازگشت", "admin:payments:pending")])
        elif payment.status == PaymentStatus.APPROVED:
            buttons.append([Button.inline("« بازگشت", "admin:payments:approved")])
        elif payment.status == PaymentStatus.REJECTED:
            buttons.append([Button.inline("« بازگشت", "admin:payments:rejected")])
        else:
            buttons.append([Button.inline("« بازگشت", "admin:payments")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_view_payment", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_payment_details(event: events.CallbackQuery.Event, payment_id: int, payment_service: PaymentService, user_service: UserService, session) -> None:
    """Handle viewing detailed payment information"""
    try:
        payment = payment_service.get_by_id(payment_id)
        
        if not payment:
            await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
            await handle_pending_payments(event, 1, payment_service, user_service)
            return
        
        # Same as handle_view_payment but with more details and potentially related info
        user_info = user_service.get_by_id(payment.user_id)
        user_name = f"{user_info.first_name} {user_info.last_name or ''}" if user_info else "کاربر ناشناس"
        
        # Get order details if there's an order attached
        order_info = ""
        if payment.order_id:
            order_service = OrderService(session)
            order = order_service.get_by_id(payment.order_id)
            if order:
                order_info = (
                    f"🛒 **اطلاعات سفارش:**\n"
                    f"شناسه سفارش: #{order.id}\n"
                    f"وضعیت سفارش: {order.status}\n"
                    f"تعداد اقلام: {order.item_count if hasattr(order, 'item_count') else 'نامشخص'}\n"
                    f"تاریخ ایجاد: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
        
        # Get payment logs
        payment_logs = payment_service.get_payment_logs(payment_id)
        logs_info = ""
        if payment_logs:
            logs_info = "📋 **تاریخچه پرداخت:**\n"
            for log in payment_logs:
                actor = "سیستم"
                if log.user_id:
                    actor_info = user_service.get_by_id(log.user_id)
                    actor = f"{actor_info.first_name} {actor_info.last_name or ''}" if actor_info else "کاربر نامشخص"
                
                logs_info += f"• {log.created_at.strftime('%Y-%m-%d %H:%M')} - {log.action} توسط {actor}\n"
            logs_info += "\n"
        
        message = (
            f"💳 **جزئیات کامل پرداخت #{payment.id}**\n\n"
            f"💰 مبلغ: {payment.amount} تومان\n"
            f"📊 وضعیت: {payment.status}\n"
            f"💭 روش پرداخت: {payment.payment_method}\n"
            f"🆔 شناسه تراکنش: {payment.transaction_id or 'ندارد'}\n\n"
            f"👤 **اطلاعات کاربر:**\n"
            f"نام: {user_name}\n"
            f"شناسه کاربری: {payment.user_id}\n"
            f"یوزرنیم: @{user_info.username if user_info and user_info.username else 'ندارد'}\n\n"
            f"{order_info}"
            f"{logs_info}"
            f"📝 توضیحات: {payment.description or 'ندارد'}\n"
            f"📅 تاریخ ایجاد: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        )
        
        # Create keyboard with action buttons
        from src.bot.keyboards.admin_keyboard import PendingPaymentsKeyboards
        keyboard = PendingPaymentsKeyboards.get_payment_actions(payment_id)
        
        await event.edit(message, buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_payment_details", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_add_payment_note(event: events.CallbackQuery.Event, payment_id: int, payment_service: PaymentService, user_service: UserService) -> None:
    """Handle adding a note to a payment"""
    try:
        payment = payment_service.get_by_id(payment_id)
        
        if not payment:
            await event.answer("پرداخت مورد نظر یافت نشد", alert=True)
            from src.bot.keyboards.admin_keyboard import get_admin_payments_keyboard
            await event.edit("💳 **مدیریت پرداخت‌ها**", buttons=get_admin_payments_keyboard())
            return
        
        message = (
            f"📝 **افزودن یادداشت به پرداخت #{payment_id}**\n\n"
            f"لطفاً یادداشت خود را برای این پرداخت وارد کنید:\n\n"
            f"یادداشت فعلی: {payment.admin_note or 'ندارد'}"
        )
        
        # Set user state to wait for payment note
        sender = await event.get_sender()
        user_service.set_user_state(sender.id, f"add_payment_note:{payment_id}")
        
        await event.edit(message, buttons=[[Button.inline("« بازگشت", f"admin:payments:details:{payment_id}")]])
    
    except Exception as e:
        log_error("Error in handle_add_payment_note", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True) 