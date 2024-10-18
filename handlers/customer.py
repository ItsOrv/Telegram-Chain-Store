from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data, update_user, create_order, confirm_payment
import config

#pass
def customer_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("خرید محصول", callback_data='customer_buy_product')],
        [InlineKeyboardButton("سبد خرید من", callback_data='customer_show_cart')],
        [InlineKeyboardButton("شارژ حساب", callback_data='customer_charge_account')],
        [InlineKeyboardButton("خریدهای قبلی", callback_data='customer_previous_orders')],
        [InlineKeyboardButton("ارتباط با مدیر", callback_data='customer_contact_admin')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['previous_step'] = None  # منوی اصلی مرحله ابتدایی است
    message = "به ربات فروش خوش آمدید"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)
#افزودن سفارش های در انتظار تایید
#pass
def customer_buy_product(update, context):
    data = load_data()
    provinces = set(product_info['province'] for product_info in data["products"].values())
    
    if provinces:
        keyboard = [[InlineKeyboardButton(province, callback_data=f"customer_province_{province}")] for province in provinces]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="customer_menu")])
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

#pass
def customer_handle_province_selection(update, context):
    data = load_data()
    query = update.callback_query
    province = query.data.split("_")[2]
    
    cities = {product_info['city'] for product_info in data["products"].values() if product_info["province"] == province}
    
    if cities:
        keyboard = [[InlineKeyboardButton(city, callback_data=f"customer_city_{city}")] for city in cities]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="customer_buy_product")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['previous_step'] = 'customer_buy_product'
        query.edit_message_text(f"شهرهای استان {province} را انتخاب کنید:", reply_markup=reply_markup)
    else:
        query.edit_message_text(f"در استان {province} هیچ شهری در دسترس نیست.")
    
    query.answer()

#pass
def customer_handle_city_selection(update, context):
    data = load_data()
    query = update.callback_query
    city = query.data.split("_")[2]

    products = [product_info for product_info in data["products"].values() if product_info["city"] == city]

    if products:
        keyboard = [
            [InlineKeyboardButton(f"{product['name']} - {product['price']} تومان", callback_data=f"customer_product_{product_id}")]
            for product_id, product in data["products"].items() if product["city"] == city
        ]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="customer_buy_product")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['previous_step'] = 'customer_buy_product'
        query.edit_message_text(f"محصولات موجود در شهر {city}:", reply_markup=reply_markup)
    else:
        query.edit_message_text(f"در شهر {city} محصولی موجود نیست.")
    
    query.answer()

#pass
def customer_handle_product_selection(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[2]

    data = load_data()
    product_info = data["products"].get(product_id)

    if product_info:
        # نمایش اطلاعات محصول
        product_details = f"📦 محصول: {product_info['name']}\n💰 قیمت: {product_info['price']} تومان\n📖 توضیحات: {product_info['description']}"

        keyboard = [
            [InlineKeyboardButton("➕ افزودن به سبد خرید", callback_data=f"add_to_cart_{product_id}")],
            [InlineKeyboardButton("بستن", callback_data="customer_cancel_product_message")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # ارسال پیام جدید با اطلاعات محصول
        query.message.reply_text(product_details, reply_markup=reply_markup)

    query.answer()

#pass  
def customer_handle_cancel_product_message(update, context):
    query = update.callback_query
    query.delete_message()
    query.answer("پیام حذف شد.")

#pass
def customer_add_product_to_cart(update, context):
    """Add a product to the customer's cart."""
    user_id = update.effective_user.id
    query = update.callback_query

    # استخراج product_id از callback_data
    product_id = query.data.split('_')[-1]
    
    # بارگذاری داده‌ها
    data = load_data()

    # بررسی وجود کاربر در دیتابیس
    user = data["users"].get(str(user_id))
    if not user:
        query.message.reply_text("شناسه کاربری شما یافت نشد، لطفاً مجدداً ثبت‌نام کنید. /start")
        return

    # بررسی اینکه کاربر مشتری است
    if user["role"] != "customer":
        query.message.reply_text("شما دسترسی به این عملیات را ندارید.")
        return

    # اطمینان از وجود محصول در دیتابیس
    product = data["products"].get(product_id)
    if not product:
        query.message.reply_text("محصول مورد نظر پیدا نشد.")
        return

    # بررسی موجودی محصول
    if product["stock"] <= 0:
        query.message.reply_text(f"محصول {product['name']} موجودی ندارد.")
        return

    # اطمینان از وجود سبد خرید برای کاربر
    if "cart" not in user:
        user["cart"] = {}

    # افزودن محصول به سبد خرید یا افزایش تعداد آن
    if product_id in user["cart"]:
        if user["cart"][product_id]["quantity"] < product["stock"]:
            user["cart"][product_id]["quantity"] += 1
            message = f"تعداد محصول {user['cart'][product_id]['name']} افزایش یافت."
        else:
            message = f"حداکثر موجودی از محصول {user['cart'][product_id]['name']} در سبد خرید قرار دارد."
    else:
        # افزودن محصول جدید به سبد خرید
        user["cart"][product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        }
        message = f"محصول {product['name']} به سبد خرید اضافه شد."

    # ذخیره‌سازی داده‌ها
    save_data(data)

    # ارسال پیام نهایی به کاربر
    query.answer()
    query.message.reply_text(message)

#pass
def customer_show_cart(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        keyboard = []
        for product_id, product_info in cart.items():
            product_button = InlineKeyboardButton(
                text=f"{product_info['name']} - قیمت: {product_info['price']} تومان - تعداد: {product_info['quantity']}",
                callback_data=f"customer_product_{product_id}"
            )
            plus_button = InlineKeyboardButton(text="➕", callback_data=f"customer_add_{product_id}")
            minus_button = InlineKeyboardButton(text="➖", callback_data=f"customer_remove_{product_id}")
            keyboard.append([product_button])
            keyboard.append([minus_button, plus_button])

        confirm_button = InlineKeyboardButton(text="تأیید سفارش", callback_data="customer_confirm_order")
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
#اضافه کردن دکمه برگشت در زیر پیام سبد خرید شما خالی است
#pass
def customer_handle_add_product(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[2]
    user_id = update.effective_user.id
    data = load_data()

    # افزایش تعداد محصول در سبد خرید
    user = data["users"].get(str(user_id), {})
    if product_id in user.get("cart", {}):
        user["cart"][product_id]["quantity"] += 1
        save_data(data)
        update_user(user_id, user)

    # بازنمایی مجدد سبد خرید بدون ارسال پیام جدید
    customer_show_cart(update, context)
    query.answer()

#pass
def customer_handle_remove_product(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[2]
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
    customer_show_cart(update, context)
    query.answer()

# دکمه رفتن به سبد خرید بعد از پیام محصول به سبد خرید اضافه شد نمایش داده شود

#pass
def customer_confirm_order(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    cart = user.get("cart", {})

    if cart:
        # محاسبه مبلغ کل
        total_amount = sum(item["price"] * item["quantity"] for item in cart.values())

        # ایجاد سفارش جدید
        order_id = create_order(user_id, cart)
        user["orders"].append({
            "order_id": order_id,
            "products": cart,\
            "status": "در انتظار تایید"
        })
        user["cart"] = {}  # خالی کردن سبد خرید پس از ثبت سفارش
        save_data(data)
        update_user(user_id, user)

        # ارسال پیام به ادمین
        admin_id = config.ADMIN_ID
        user_full_name = update.effective_user.full_name
        context.bot.send_message(chat_id=admin_id, text=f"سفارشی از طرف کاربر {user_full_name} (شناسه: {user_id}) در انتظار پرداخت است.")

        # نمایش گزینه‌های پرداخت به کاربر
        keyboard = [
            [InlineKeyboardButton("کارت به کارت", callback_data="customer_card_to_card_payment")],
            [InlineKeyboardButton("پرداخت با کریپتو", callback_data="customer_crypto_payment")],
            [InlineKeyboardButton("پرداخت با موجودی", callback_data="customer_pay_with_balance")],
            [InlineKeyboardButton("لغو", callback_data="customer_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.callback_query.message.reply_text(f"سفارش شما با شناسه {order_id} ثبت شد.\n مبلغ کل: {total_amount} تومان.\n لطفاً روش پرداخت خود را انتخاب کنید:", reply_markup=reply_markup)
    else:
        update.callback_query.message.reply_text("سبد خرید شما خالی است.")
    
    update.callback_query.answer()

#pass
def customer_card_to_card_payment(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data["users"].get(str(user_id), {})
    pending_order = next((order for order in user.get("orders", []) if order["status"] == "در انتظار تایید"), None)

    if pending_order:
        # دریافت PAYMENT_ID از تنظیمات
        payment_id = getattr(config, 'PAYMENT_ID', "@defaultusername")
        total_amount = sum(item["price"] * item["quantity"] for item in pending_order["products"].values())
        
        # نمایش پیام و درخواست ارسال تصویر فیش واریزی
        message = f"لطفاً به آیدی {payment_id} پیام دهید تا شماره کارت دریافت کنید.\nسپس تصویر فیش واریزی به مبلغ {total_amount} تومان را همینجا ارسال کنید." #مبلغ کل رو هم اینجا به کاربر نشون بده
        keyboard = [[InlineKeyboardButton("کنسل کردن", callback_data="customer_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

        # ذخیره وضعیت انتظار برای پرداخت کارت به کارت
        context.user_data['awaiting_card_payment'] = True
        context.user_data['pending_order_id'] = pending_order["order_id"]
        context.user_data['awaiting_receipt_photo'] = True
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="هیچ سفارشی در انتظار تایید پرداخت وجود ندارد.")

#pass
def handle_payment_confirmation(update, context):
    if context.user_data.get('awaiting_receipt_photo') and update.message.photo:
        user_id = update.effective_user.id
        photo = update.message.photo[-1].file_id  # دریافت فیش واریزی (آخرین عکس)
        order_id = context.user_data.get('pending_order_id')

        if order_id:
            # ارسال تصویر فیش به ادمین همراه با دکمه تایید و لغو
            keyboard = [
                [InlineKeyboardButton("تایید", callback_data=f"confirm_payment_{order_id}_{user_id}")],
                [InlineKeyboardButton("لغو", callback_data=f"reject_payment_{order_id}_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            admin_id = getattr(config, 'ADMIN_ID', None)
            if admin_id:
                context.bot.send_photo(chat_id=admin_id, photo=photo, caption=f"فیش واریزی از کاربر {user_id} برای سفارش {order_id}:", reply_markup=reply_markup)
                context.bot.send_message(chat_id=update.effective_chat.id, text="فیش واریزی شما ارسال شد و در حال بررسی است.")
                context.user_data['awaiting_receipt_photo'] = False  # غیرفعال کردن حالت انتظار پس از ارسال تصویر
            else:
                update.message.reply_text("خطای آیدی مدیر.")
        else:
            update.message.reply_text("خطا در دریافت شناسه سفارش.")
    else:
        update.message.reply_text("خطایی در پردازش تصویر فیش واریزی اتفاق افتاد.")


def handle_admin_decision(update, context):
    print("handling pass")
    query = update.callback_query
    query_data = query.data.split('_')
    #print(query_data)
    action = query_data[0]
    #print(action)  # 'confirm_payment' یا 'reject_payment'
    order_id = query_data[2]
    #print(order_id)
    user_id = query_data[3]
    #print(user_id)

    if action == "confirm":
        confirm_payment(user_id, order_id)
        context.bot.send_message(chat_id=user_id, text=f"پرداخت شما تایید شد. سفارش شما با شناسه {order_id} در حال پردازش است.")
        query.message.edit_caption(caption=f"فیش واریزی از کاربر {user_id} برای سفارش {order_id}: (تایید شد)")

    elif action == "reject":
        cancel_order(user_id, order_id)
        context.bot.send_message(chat_id=user_id, text="پرداخت شما تایید نشد. سفارش شما لغو شده است.")
        query.message.edit_caption(caption=f"فیش واریزی از کاربر {user_id} برای سفارش {order_id}: (لغو شد)")

    query.answer()

# تایید پرداخت و پردازش سفارش
def confirm_payment(user_id, order_id):
    data = load_data()
    user = data["users"].get(str(user_id), {})
    order = next((order for order in user.get("orders", []) if order["order_id"] == order_id), None)

    if order:
        order["status"] = "پرداخت شده"
        save_data(data)
        update_user(user_id, user)

        # آماده کردن لیست خرید برای ارسال به ادمین
        products_list = []
        for product in order["products"]:
            product_name = product["name"]
            agent_id = product.get("agent_id")  # شناسه نماینده محصول
            products_list.append(f"محصول: {product_name}, نماینده: {agent_id}")

        # تبدیل لیست محصولات به رشته برای پیام
        product_info = "\n".join(products_list)

        # ارسال پیام به ادمین با لیست محصولات
        admin_id = getattr(config, 'ADMIN_ID', None)
        if admin_id:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"سفارش {order_id} تایید شد.\nلیست محصولات:\n{product_info}"
            )

        # فراخوانی فانکشنی برای پردازش سفارش (می‌توانید این را سفارشی کنید)
        process_order(order_id)


# لغو سفارش
def cancel_order(user_id, order_id):
    data = load_data()
    user = data["users"].get(str(user_id), {})
    order = next((order for order in user.get("orders", []) if order["order_id"] == order_id), None)

    if order:
        # آماده کردن لیست خرید برای ارسال به ادمین
        products_list = []
        for product in order["products"]:
            product_name = product["name"]
            agent_id = product.get("agent_id")  # شناسه نماینده محصول
            products_list.append(f"محصول: {product_name}, نماینده: {agent_id}")

        # تبدیل لیست محصولات به رشته برای پیام
        product_info = "\n".join(products_list)

        # ارسال پیام به ادمین با لیست محصولات
        admin_id = getattr(config, 'ADMIN_ID', None)
        if admin_id:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"سفارش {order_id} لغو شد.\nلیست محصولات:\n{product_info}"
            )

        # حذف سفارش از لیست کاربر
        user["orders"] = [o for o in user.get("orders", []) if o["order_id"] != order_id]
        save_data(data)
        update_user(user_id, user)


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

