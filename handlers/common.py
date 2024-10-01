from utils.helpers import load_data, update_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    """بررسی نقش کاربر و نمایش منوی مناسب."""
    user_id = str(update.message.from_user.id)  # تبدیل به رشته برای کلید دیکشنری
    data = load_data()
    
    # بررسی وجود کاربر در دیتابیس
    user = data["users"].get(user_id)
    
    # اگر کاربر جدید است، اطلاعات اولیه کاربر را اضافه می‌کنیم
    if not user:
        new_user = {
            "role": "customer",  # نقش پیش‌فرض برای کاربر جدید
            "balance": 0,  # شارژ اولیه حساب
            "city": "",  # شهر پیش‌فرض (می‌تواند بعداً توسط کاربر تعیین شود)
            "cart": {},  # سبد خرید خالی
            "orders": []  # لیست سفارشات
        }
        data["users"][user_id] = new_user
        update_user(user_id, new_user)  # ذخیره‌سازی کاربر جدید

    # بررسی نقش کاربر و هدایت به منوی مناسب
    if user and user.get("role") == "admin":
        from handlers.admin import admin_menu
        admin_menu(update, context)
    elif user and user.get("role") == "agent":
        from handlers.agent import agent_menu
        agent_menu(update, context)
    else:
        from handlers.customer import customer_menu
        customer_menu(update, context)


from utils.helpers import load_data, update_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    user_id = update.message.from_user.id
    data = load_data()
    user = data["users"].get(str(user_id))

    if not user:
        new_user = {
            "role": "customer",
            "balance": 0,
            "city": "",
            "cart": {},
            "orders": []
        }
        data["users"][str(user_id)] = new_user
        update_user(user_id, new_user)

    if user and user["role"] == "admin":
        from handlers.admin import admin_menu
        admin_menu(update, context)
    elif user and user["role"] == "agent":
        from handlers.agent import agent_menu
        agent_menu(update, context)
    else:
        from handlers.customer import customer_menu
        customer_menu(update, context)

def handle_message(update, context):
    user_id = update.effective_user.id
    state = context.user_data.get('state')

    if state == 'adding_product':
        agent.handle_new_product(update, context)
    elif state == 'adding_category':
        admin.handle_new_category(update, context)
    elif state == 'charging':
        customer.handle_charge_account(update, context)
    else:
        update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید.")
