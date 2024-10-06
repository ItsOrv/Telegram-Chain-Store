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

    context.user_data['previous_step'] = None  # منوی اصلی مرحله ابتدایی است

    if update.message:
        update.message.reply_text("به ربات فروش خوش آمدید", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text("به ربات فروش خوش آمدید", reply_markup=reply_markup)
        update.callback_query.answer()

# شروع خرید محصول مرحله ۱:
def buy_product(update, context):
    data = load_data()
    provinces = set(product_info['province'] for product_info in data["products"].values())
    
    if provinces:
        keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in provinces]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['previous_step'] = 'main_menu'
        
        if update.message:
            update.message.reply_text("لطفاً استان خود را انتخاب کنید:", reply_markup=reply_markup)
        elif update.callback_query:
            update.callback_query.edit_message_text("لطفاً استان خود را انتخاب کنید:", reply_markup=reply_markup)
            update.callback_query.answer()
    else:
        message = "هیچ استانی در دسترس نیست."
        if update.message:
            update.message.reply_text(message)
        elif update.callback_query:
            update.callback_query.edit_message_text(message)
            update.callback_query.answer()


# مرحله 2: نمایش شهرهای مرتبط با استان انتخاب‌شده
def handle_province_selection(update, context):
    data = load_data()
    query = update.callback_query
    province = query.data.split("_")[1]
    
    cities = {product_info['city'] for product_info in data["products"].values() if product_info["province"] == province}
    
    if cities:
        keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_buy_product")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['previous_step'] = 'buy_product'
        query.edit_message_text(f"شهرهای استان {province} را انتخاب کنید:", reply_markup=reply_markup)
    else:
        query.edit_message_text(f"در استان {province} هیچ شهری در دسترس نیست.")
    
    query.answer()


# مرحله 3: نمایش لیست محصولات در شهر انتخابی
def handle_city_selection(update, context):
    data = load_data()
    query = update.callback_query
    city = query.data.split("_")[1]

    products = [product_info for product_info in data["products"].values() if product_info["city"] == city]

    if products:
        keyboard = [
            [InlineKeyboardButton(f"{product['name']} - {product['price']} تومان", callback_data=f"product_{product_id}")]
            for product_id, product in data["products"].items() if product["city"] == city
        ]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['previous_step'] = 'handle_province_selection'
        query.edit_message_text(f"محصولات موجود در شهر {city}:", reply_markup=reply_markup)
    else:
        query.edit_message_text(f"در شهر {city} محصولی موجود نیست.")
    
    query.answer()


# مرحله 4: نمایش اطلاعات محصول انتخابی
def handle_product_selection(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]

    data = load_data()
    product_info = data["products"].get(product_id)

    if product_info:
        # نمایش اطلاعات محصول
        product_details = f"📦 محصول: {product_info['name']}\n💰 قیمت: {product_info['price']} تومان\n📖 توضیحات: {product_info['description']}"

        keyboard = [
            [InlineKeyboardButton("➕ افزودن به سبد خرید", callback_data=f"add_to_cart_{product_id}")],
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_product_message")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # ارسال پیام جدید با اطلاعات محصول
        query.message.reply_text(product_details, reply_markup=reply_markup)

    query.answer()


    
def handle_cancel_product_message(update, context):
    query = update.callback_query
    query.delete_message()
    query.answer("پیام حذف شد.")


def show_product_details(update, context, product_id):
    query = update.callback_query
    data = load_data()
    product_info = data["products"].get(product_id)

    if product_info:
        product_message = f"نام محصول: {product_info['name']}\n" \
                          f"قیمت: {product_info['price']}\n" \
                          f"توضیحات: {product_info['description']}\n" 
                          #f"موجودی: {product_info['inventory']}\n"

        # ارسال پیام جدید با اطلاعات محصول
        context.bot.send_message(chat_id=query.message.chat_id, text=product_message)

        # دکمه‌های افزودن به سبد خرید و لغو
        keyboard = [
            [InlineKeyboardButton("➕ افزودن به سبد خرید", callback_data=f"add_to_cart_{product_id}")],
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_product_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # ارسال دکمه‌ها در زیر پیام
        context.bot.send_message(chat_id=query.message.chat_id, text="لطفا اقدام خود را انتخاب کنید:", reply_markup=reply_markup)

        # حذف پیام قبلی (لیست محصولات)
        
    query.answer()


# افزودن محصول به سبد خرید
def add_product_to_cart(update, context, product_id):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id))

    if user:
        # اطمینان از وجود سبد خرید برای کاربر
        if "cart" not in user:
            user["cart"] = {}

        # در صورت موجود بودن محصول در سبد خرید
        if product_id in user["cart"]:
            user["cart"][product_id]["quantity"] += 1
            message = f"تعداد محصول {user['cart'][product_id]['name']} افزایش یافت."
        else:
            # در صورت موچود نبودن محصول در سبد خرید کاربر
            product_info = data["products"].get(product_id)
            if product_info:
                user["cart"][product_id] = {
                    "name": product_info["name"],
                    "price": product_info["price"],
                    "quantity": 1
                }
                message = f"محصول {product_info['name']} به سبد خرید اضافه شد."
            else:
                message = "محصول مورد نظر پیدا نشد."
                if update.message:
                    update.message.reply_text(message)
                elif update.callback_query:
                    update.callback_query.message.reply_text(message)
                return

        save_data(data)
        update_user(user_id, user)

        if update.message:
            update.message.reply_text(message)
        elif update.callback_query:
            update.callback_query.message.reply_text(message)

    else:
        # اگر کاربر در دیتابیس موجود نباشد
        if update.message:
            update.message.reply_text("ایدی کاربری شما در دیتابیس یافت نشد، لطفا ربات را دوباره راه اندازی کنید و با مدیر در ارتباط باشید. \n /start")
        elif update.callback_query:
            update.callback_query.message.reply_text("ایدی کاربری شما در دیتابیس یافت نشد، لطفا ربات را دوباره راه اندازی کنید و با مدیر در ارتباط باشید. \n /start")


# نمایش سبد خرید با دکمه‌های شیشه‌ای
def show_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        keyboard = []
        for product_id, product_info in cart.items():
            product_button = InlineKeyboardButton(
                text=f"{product_info['name']} - قیمت: {product_info['price']} تومان - تعداد: {product_info['quantity']}",
                callback_data=f"product_{product_id}"
            )
            plus_button = InlineKeyboardButton(text="➕", callback_data=f"add_{product_id}")
            minus_button = InlineKeyboardButton(text="➖", callback_data=f"remove_{product_id}")
            keyboard.append([product_button])
            keyboard.append([minus_button, plus_button])

        confirm_button = InlineKeyboardButton(text="تأیید سفارش", callback_data="confirm_order")
        keyboard.append([confirm_button])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            update.message.reply_text("سبد خرید شما:", reply_markup=reply_markup)
        elif update.callback_query:
            update.callback_query.edit_message_text("سبد خرید شما:", reply_markup=reply_markup)
            update.callback_query.answer()
    else:
        message = "سبد خرید شما خالی است."
        if update.message:
            update.message.reply_text(message)
        elif update.callback_query:
            update.callback_query.edit_message_text(message)
            update.callback_query.answer()


# هندلر برای افزایش تعداد محصول
def handle_add_product(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    user_id = update.effective_user.id
    data = load_data()

    # افزایش تعداد محصول در سبد خرید
    user = data["users"].get(str(user_id), {})
    if product_id in user.get("cart", {}):
        user["cart"][product_id]["quantity"] += 1
        save_data(data)
        update_user(user_id, user)

    # بازنمایی مجدد سبد خرید بدون ارسال پیام جدید
    show_cart(update, context)
    query.answer()

# هندلر برای کاهش تعداد محصول
def handle_remove_product(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    user_id = update.effective_user.id
    data = load_data()

    # کاهش تعداد محصول در سبد خرید
    user = data["users"].get(str(user_id), {})
    if product_id in user.get("cart", {}):
        if user["cart"][product_id]["quantity"] > 1:
            user["cart"][product_id]["quantity"] -= 1
        else:
            # اگر تعداد به 0 برسد، محصول را از سبد خرید حذف می‌کنیم
            del user["cart"][product_id]
        save_data(data)
        update_user(user_id, user)

    # بازنمایی مجدد سبد خرید بدون ارسال پیام جدید
    show_cart(update, context)
    query.answer()

# تأیید سفارش
"""
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
"""


# نمایش خریدهای قبلی
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







# حذف محصول از سبد خرید
def remove_from_cart(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})

    if product_id in user.get("cart", {}):
        del user["cart"][product_id]
        save_data(data)
        update_user(user_id, user)
        query.message.reply_text("محصول از سبد خرید شما حذف شد.")
    else:
        query.message.reply_text("محصول مورد نظر در سبد خرید شما یافت نشد.")
    query.answer()



# پرداخت کارت به کارت
def card_to_card_payment(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})

    if user.get("cart"):
        query.message.reply_text("لطفاً فیش واریزی خود را به این آیدی ارسال کنید: {config.PAYMENT_CONFIRMATION_ID}")
        context.user_data['awaiting_payment_confirmation'] = True
    else:
        query.message.reply_text("سبد خرید شما خالی است.")
    query.answer()


# دریافت فیش واریزی و تایید سفارش
def handle_payment_confirmation(update, context):
    if context.user_data.get('awaiting_payment_confirmation'):
        if update.message.photo:  # اگر عکس ارسال شد
            user_id = update.effective_user.id
            photo = update.message.photo[-1].file_id
            context.bot.send_photo(chat_id=config.PAYMENT_CONFIRMATION_ID, photo=photo, caption=f"فیش واریزی از کاربر {user_id}")
            confirm_payment(user_id)
            update.message.reply_text("فیش واریزی شما ارسال شد و در حال بررسی است.")
            context.user_data['awaiting_payment_confirmation'] = False
        else:
            update.message.reply_text("لطفاً فیش واریزی خود را به صورت عکس ارسال کنید.")



# پرداخت کریپتو (به صورت پایه‌ای)
def crypto_payment(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})

    if user.get("cart"):
        query.message.reply_text("برای پرداخت با کریپتو، لطفاً به این آدرس مبلغ را ارسال کنید: {config.CRYPTO_PAYMENT_ADDRESS}")
        context.user_data['awaiting_crypto_payment'] = True
    else:
        query.message.reply_text("سبد خرید شما خالی است.")
    query.answer()



# تایید پرداخت کریپتو
def handle_crypto_confirmation(update, context):
    if context.user_data.get('awaiting_crypto_payment'):
        transaction_id = update.message.text  # فرض می‌کنیم کاربر شناسه تراکنش را ارسال می‌کند
        if transaction_id:
            user_id = update.effective_user.id
            context.bot.send_message(chat_id=config.PAYMENT_CONFIRMATION_ID, text=f"پرداخت کریپتو از کاربر {user_id}: {transaction_id}")
            confirm_payment(user_id)
            update.message.reply_text("پرداخت کریپتوی شما دریافت شد و سفارش شما تایید شده است.")
            context.user_data['awaiting_crypto_payment'] = False
        else:
            update.message.reply_text("لطفاً شناسه تراکنش کریپتو را ارسال کنید.")



# تایید نهایی سفارش و ارسال اطلاعات به ادمین‌ها
def confirm_payment(user_id):
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})
    
    if cart:
        order_id = create_order(user_id, cart)
        user["orders"].append({
            "order_id": order_id,
            "products": cart,
            "status": "پرداخت شده"
        })
        user["cart"] = {}  # خالی کردن سبد خرید پس از تایید پرداخت
        save_data(data)
        update_user(user_id, user)

        # ارسال پیام به نماینده و ادمین‌ها
        for product_id in cart:
            product_info = data["products"][product_id]
            agent_id = product_info["agent_id"]
            context.bot.send_message(chat_id=agent_id, text=f"سفارش جدید از کاربر {user_id}: {product_info['name']}")

        # ارسال پیام تایید به کاربر
        context.bot.send_message(chat_id=user_id, text=f"سفارش شما با شناسه {order_id} تایید شد. با تشکر از خرید شما.")
        context.bot.send_message(chat_id=config.PAYMENT_CONFIRMATION_ID, text=f"سفارش کاربر {user_id} تایید شد.")


# بازگشت به مرحله قبل
def go_back(update, context):
    query = update.callback_query
    previous_step = context.user_data.get('previous_step')
    
    if previous_step == 'main_menu':
        customer_menu(update, context)
    elif previous_step == 'buy_product':
        buy_product(update, context)
    elif previous_step == 'handle_province_selection':
        handle_province_selection(update, context)
    elif previous_step == 'handle_city_selection':
        handle_city_selection(update, context)
    # مراحل دیگر را به همین ترتیب اضافه کنید
    
    query.answer()

def handle_back(update, context):
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "back_to_main_menu":
        customer_menu(update, context)
    elif callback_data == "back_to_buy_product":
        buy_product(update, context)
    elif callback_data == "back_to_province_selection":
        handle_province_selection(update, context)
    elif callback_data == "x":
        handle_city_selection(update, context)
    elif callback_data == "back_to_product_list":
        handle_product_selection(update, context)
    
    query.answer()






"""
- خرید محصول
    انتخاب دسته بندی
    انتخاب استان
    انتخاب شهر
    (نمایش لیست محصولات ان شهر و استان و دسته بندی)
    انتخاب محصول
    دیدن مشخصات  محصول
        مشخصات محصول
        مشخصات نماینده اراعه دهنده
        امتیاز محصول
        نظرات
            مشاهده نظرات به صورت سه تا سه تا 
                صفحه بعد و قبل
        افزودن به سبد خرید
            اضافه کردن به سبد خرید و ادامه خرید
            ثبت نهایی و رفتن به سبد خرید
- سبد خرید من 
(نمایش محصولات در سبد خرید به صورت دکمه شیشه ای)
    افزودن محصول
        رفتن به خرید محصول
    خرید نهایی
        نمایش مبلغ و توضیحات همراه گزینه های پرداخت
            پرداخت با موجودی
                تولید کد پیگیری سفارش و افزودن به دیتابیس
                ارسال پیام سفارش جدید به نماینده های اراعه دهنده محصول خریداری شده
                ارسال پیام تایید خرید به مشتری همراه با کد پیگیری و ایدی ادمین مربوطه
                ارسال پیام به ادمین اصلی حاوی اطلاعات کامل خرید و اطلاعات کامل پیگیری سفارش
                اضافه شدن محصولات به خرید های قبلی
            کارت به کارت
                درخواست ارسال فیش واریزی
                    ارسال فیش واریزی به مدیر اصلی
                        تایید 
                            تولید کد پیگیری سفارش و افزودن به دیتابیس
                            ارسال پیام سفارش جدید به نماینده های اراعه دهنده محصول خریداری شده
                            ارسال پیام تایید خرید به مشتری همراه با کد پیگیری و ایدی ادمین مربوطه
                            ارسال پیام به ادمین اصلی حاوی اطلاعات کامل خرید و اطلاعات کامل پیگیری سفارش
                            اضافه شدن محصولات به خرید های قبلی
                        لغو
                            ارسال پیام لغو خرید به مشتری
            پرداخت کریپتو
                ؟
- شارژ حساب
    کارت به کارت
        درخواست ارسال فیش واریزی
            ارسال فیش واریزی به مدیر اصلی
                تایید 
                    افزایش موجودی کاربر
                    ارسال پیام تایید افزایش موجودی همراه با موجودی جدید کاربر و مبلغ اضافه شده
                لغو
                    ارسال پیام عدم تایید افزایش موجودی
    پرداخت کریپتو
                ؟
- خریدهای قبلی

- ارتباط با مدیر

"""

