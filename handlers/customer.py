from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data, add_product_to_cart, create_order, confirm_payment
import config

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
        update.callback_query.message.reply_text("به ربات خانه فروش خوش آمدید", reply_markup=reply_markup)
        update.callback_query.answer()

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

def buy_product(update, context):
    # مرحله 1: نمایش لیست استان‌ها
    data = load_data()
    provinces = set([agent_info['province'] for agent_info in data["agents"].values()])
    keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in provinces]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text("استان خود را انتخاب کنید.", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text("استان خود را انتخاب کنید.", reply_markup=reply_markup)
        update.callback_query.answer()

def handle_province_selection(update, context):
    # مرحله 2: پس از انتخاب استان، نمایش لیست شهرها
    data = load_data()
    query = update.callback_query
    province = query.data.split("_")[1]  # استخراج نام استان از callback_data
    cities = [city for city, agent_info in data["agents"].items() if agent_info["province"] == province]
    
    if cities:
        keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(f"شهرهای استان {province} را انتخاب کنید:", reply_markup=reply_markup)
    else:
        query.message.reply_text(f"در استان {province} شهری ثبت نشده است.")
    
    query.answer()

def handle_city_selection(update, context):
    # مرحله 3: پس از انتخاب شهر، نمایش لیست محصولات
    data = load_data()
    query = update.callback_query
    city = query.data.split("_")[1]  # استخراج نام شهر از callback_data

    # استخراج محصولات نماینده‌ها در شهر انتخاب‌شده
    agent_info = data["agents"].get(city, {})
    products = agent_info.get("products", [])
    
    if products:
        keyboard = [[InlineKeyboardButton(product, callback_data=f"product_{product}")] for product in products]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(f"محصولات شهر {city}:", reply_markup=reply_markup)
    else:
        query.message.reply_text(f"در شهر {city} محصولی موجود نیست.")
    
    query.answer()

def handle_product_selection(update, context):
    # مرحله 4: نمایش اطلاعات محصول انتخابی
    query = update.callback_query
    product = query.data.split("_")[1]  # استخراج نام محصول از callback_data
    
    # فرض کنید اطلاعات دقیق محصول در فایل JSON ذخیره شده باشد
    data = load_data()
    product_info = next((p for agent in data['agents'].values() for p in agent['products'] if p == product), None)
    
    if product_info:
        query.message.reply_text(f"اطلاعات محصول {product}:\n{product_info}")
    else:
        query.message.reply_text(f"محصول {product} پیدا نشد.")
    
    query.answer()


def show_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        message = "سبد خرید شما:\n"
        for product_id, product_info in cart.items():
            message += f"{product_info['name']} - تعداد: {product_info['quantity']} - قیمت: {product_info['price']} تومان\n"
    else:
        message = "سبد خرید شما خالی است."

    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()

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

def charge_account(update, context):
    if update.message:
        context.bot.send_message(chat_id=update.effective_chat.id, text="لطفاً مبلغ را وارد کنید.")
        context.user_data['charging'] = True
    elif update.callback_query:
        update.callback_query.message.reply_text("لطفاً مبلغ را وارد کنید.")
        update.callback_query.answer()
        context.user_data['charging'] = True

def contact_admin(update, context):
    message = f"مدیریت ربات: \n {config.PAYMENT_CONFIRMATION_ID}"
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()

def handle_message(update, context):
    user_id = update.effective_user.id
    if context.user_data.get('charging'):
        amount = update.message.text
        if amount.isdigit():
            charge_account(user_id, int(amount))  # فرض بر این است که تابع charge_account برای شارژ حساب وجود دارد
            update.message.reply_text(f"حساب شما به مبلغ {amount} تومان شارژ شد.")
            context.user_data['charging'] = False
        else:
            update.message.reply_text("لطفاً یک مقدار معتبر وارد کنید.")
    else:
        update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید.")

def charge_account(user_id, amount):
    data = load_data()
    user = data["users"][str(user_id)]
    user["balance"] += amount
    update_user(user_id, user)

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_product_to_cart(update, context, product_id):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id))

    if user:
        if "cart" not in user:
            user["cart"] = {}
        if product_id in user["cart"]:
            user["cart"][product_id]["quantity"] += 1  # افزایش مقدار محصول در سبد خرید
        else:
            # فرض بر این است که اطلاعات محصول در data["products"] وجود دارد
            product_info = data["products"].get(product_id)
            user["cart"][product_id] = {
                "name": product_info["name"],
                "price": product_info["price"],
                "quantity": 1
            }
        save_data(data)
        update.message.reply_text(f"محصول {product_info['name']} به سبد خرید شما اضافه شد.")
    else:
        update.message.reply_text("کاربر یافت نشد.")

def view_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        message = "سبد خرید شما:\n"
        for product_id, product_info in cart.items():
            message += f"{product_info['name']} - تعداد: {product_info['quantity']} - قیمت: {product_info['price']} تومان\n"
        message += "\n[حذف کردن محصول](remove_from_cart) یا [تأیید سفارش](confirm_order)"
    else:
        message = "سبد خرید شما خالی است."

    if update.message:
        update.message.reply_text(message, disable_web_page_preview=True)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, disable_web_page_preview=True)
        update.callback_query.answer()

def remove_from_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        product_id = update.callback_query.data.split('_')[2]  # استخراج شناسه محصول از callback data
        if product_id in cart:
            del cart[product_id]  # حذف محصول از سبد خرید
            update.callback_query.message.reply_text(f"محصول با شناسه {product_id} از سبد خرید شما حذف شد.")
            save_data(data)
        else:
            update.callback_query.message.reply_text("این محصول در سبد خرید شما وجود ندارد.")
        update.callback_query.answer()
    else:
        update.callback_query.message.reply_text("سبد خرید شما خالی است.")
        update.callback_query.answer()

def confirm_order(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        order_id = create_order(user_id, cart)  # تابعی برای ایجاد سفارش
        user["orders"].append({"order_id": order_id, "products": cart, "status": "تأیید شده"})
        user["cart"] = {}  # خالی کردن سبد خرید پس از تأیید
        save_data(data)
        update.callback_query.message.reply_text(f"سفارش شما با شناسه {order_id} تأیید شد.")
    else:
        update.callback_query.message.reply_text("سبد خرید شما خالی است.")
    update.callback_query.answer()

def handle_product_selection(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]  # فرض می‌کنیم که داده callback به صورت 'product_product_id' است
    data = load_data()
    product = data["products"].get(product_id)

    if product:
        # اضافه کردن محصول به سبد خرید
        add_product_to_cart(update, context, product_id)
        query.answer()
        query.message.reply_text(f"محصول {product['name']} به سبد خرید شما اضافه شد.")
    else:
        query.answer()
        query.message.reply_text("محصولی با این شناسه پیدا نشد.")
