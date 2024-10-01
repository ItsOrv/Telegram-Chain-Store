from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data, update_user, create_order, confirm_payment
import config


# تابع نمایش منوی اصلی مشتری
def customer_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("خرید محصول", callback_data='buy_product')],
        [InlineKeyboardButton("سبد خرید من", callback_data='show_cart')],
        [InlineKeyboardButton("شارژ حساب", callback_data='charge_account')],
        [InlineKeyboardButton("خریدهای قبلی", callback_data='previous_orders')],
        [InlineKeyboardButton("ارتباط با مدیر", callback_data='contact_admin')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text("به ربات فروش خوش آمدید", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text("به ربات فروش خوش آمدید", reply_markup=reply_markup)
        update.callback_query.answer()


# مرحله 1: نمایش لیست استان‌ها
def buy_product(update, context):
    data = load_data()
    provinces = set(agent_info['province'] for agent_info in data["agents"].values())
    
    if provinces:
        keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in provinces]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            update.message.reply_text("لطفاً استان خود را انتخاب کنید:", reply_markup=reply_markup)
        elif update.callback_query:
            update.callback_query.message.reply_text("لطفاً استان خود را انتخاب کنید:", reply_markup=reply_markup)
            update.callback_query.answer()
    else:
        update.message.reply_text("هیچ استانی ثبت نشده است.")


# مرحله 2: نمایش شهرهای انتخاب‌شده
def handle_province_selection(update, context):
    data = load_data()
    query = update.callback_query
    province = query.data.split("_")[1]
    cities = [city for city, agent_info in data["agents"].items() if agent_info["province"] == province]
    
    if cities:
        keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(f"شهرهای استان {province} را انتخاب کنید:", reply_markup=reply_markup)
    else:
        query.message.reply_text(f"در استان {province} شهری ثبت نشده است.")
    query.answer()


# مرحله 3: نمایش لیست محصولات در شهر انتخابی
def handle_city_selection(update, context):
    data = load_data()
    query = update.callback_query
    city = query.data.split("_")[1]

    agent_info = data["agents"].get(city, {})
    products = agent_info.get("products", [])
    
    if products:
        keyboard = [[InlineKeyboardButton(product, callback_data=f"product_{product}")] for product in products]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(f"محصولات موجود در شهر {city}:", reply_markup=reply_markup)
    else:
        query.message.reply_text(f"در شهر {city} محصولی موجود نیست.")
    
    query.answer()


# مرحله 4: نمایش اطلاعات محصول انتخابی و افزودن به سبد خرید
def handle_product_selection(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    data = load_data()
    product = next((p for agent in data['agents'].values() for p in agent['products'] if p == product_id), None)

    if product:
        add_product_to_cart(update, context, product_id)
        query.message.reply_text(f"محصول {product} به سبد خرید شما اضافه شد.")
    else:
        query.message.reply_text(f"محصول {product_id} یافت نشد.")
    query.answer()


# افزودن محصول به سبد خرید
def add_product_to_cart(update, context, product_id):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id))

    if user:
        if "cart" not in user:
            user["cart"] = {}
        if product_id in user["cart"]:
            user["cart"][product_id]["quantity"] += 1
        else:
            product_info = data["products"].get(product_id)
            if product_info:
                user["cart"][product_id] = {
                    "name": product_info["name"],
                    "price": product_info["price"],
                    "quantity": 1
                }
            else:
                update.message.reply_text("محصول مورد نظر پیدا نشد.")
                return

        save_data(data)
        update_user(user_id, user)
        update.message.reply_text(f"محصول {product_info['name']} به سبد خرید اضافه شد.")
    else:
        update.message.reply_text("کاربر یافت نشد.")


# نمایش سبد خرید
def show_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        message = "سبد خرید شما:\n"
        for product_id, product_info in cart.items():
            message += f"{product_info['name']} - تعداد: {product_info['quantity']} - قیمت: {product_info['price']} تومان\n"
        message += "\nبرای [حذف محصول](remove_from_cart) یا [تأیید سفارش](confirm_order) کلیک کنید."
    else:
        message = "سبد خرید شما خالی است."

    if update.message:
        update.message.reply_text(message, disable_web_page_preview=True)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, disable_web_page_preview=True)
        update.callback_query.answer()


# تأیید سفارش
def confirm_order(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        order_id = create_order(user_id, cart)
        user["orders"].append({
            "order_id": order_id,
            "products": cart,
            "status": "تأیید شده"
        })
        user["cart"] = {}  # خالی کردن سبد پس از تأیید
        save_data(data)
        update_user(user_id, user)
        update.callback_query.message.reply_text(f"سفارش شما با شناسه {order_id} تأیید شد.")
    else:
        update.callback_query.message.reply_text("سبد خرید شما خالی است.")
    
    update.callback_query.answer()


# نمایش خریدهای قبلی
def previous_orders(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})

    if user.get("orders"):
        message = "خریدهای قبلی شما:\n"
        for order in user["orders"]:
            products = "\n".join([f"- {p['name']} (تعداد: {p['quantity']})" for p in order["products"].values()])
            message += f"سفارش {order['order_id']} - وضعیت: {order['status']}\n{products}\n"
    else:
        message = "شما هیچ خریدی نداشته‌اید."

    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()


# شارژ حساب
def charge_account(update, context):
    if update.message:
        context.bot.send_message(chat_id=update.effective_chat.id, text="لطفاً مبلغ را وارد کنید.")
        context.user_data['charging'] = True
    elif update.callback_query:
        update.callback_query.message.reply_text("لطفاً مبلغ را وارد کنید.")
        context.user_data['charging'] = True
        update.callback_query.answer()


# دریافت مبلغ و شارژ حساب
def handle_message(update, context):
    user_id = update.effective_user.id
    if context.user_data.get('charging'):
        amount = update.message.text
        if amount.isdigit():
            charge_user_account(user_id, int(amount))
            update.message.reply_text(f"حساب شما به مبلغ {amount} تومان شارژ شد.")
            context.user_data['charging'] = False
        else:
            update.message.reply_text("لطفاً مبلغ معتبر وارد کنید.")
    else:
        update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید.")


# شارژ حساب کاربری
def charge_user_account(user_id, amount):
    data = load_data()
    user = data["users"][str(user_id)]
    user["balance"] += amount
    save_data(data)
    update_user(user_id, user)


# ارتباط با مدیر
def contact_admin(update, context):
    message = f"مدیریت ربات: \n {config.PAYMENT_CONFIRMATION_ID}"
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()
