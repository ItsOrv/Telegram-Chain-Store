from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

#pass
def admin_menu(update, context):
    """نمایش منوی اصلی ادمین."""
    keyboard = [
        [InlineKeyboardButton("مدیریت دسته‌بندی‌ها", callback_data='manage_categories')],
        [InlineKeyboardButton("مدیریت محصولات و نماینده‌ها", callback_data='list_agents')],
        [InlineKeyboardButton("افزودن نماینده", callback_data='add_agent_start')],
        [InlineKeyboardButton("گزارش‌گیری", callback_data='reports')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "به پنل ادمین خوش آمدید"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def manage_categories(update, context):
    """مدیریت دسته‌بندی‌ها و نمایش دکمه‌های مربوطه."""
    data = load_data()
    categories = data.get("categories", [])

    keyboard = [[InlineKeyboardButton("افزودن دسته‌بندی", callback_data='add_category')]]
    for category in categories:
        keyboard.append([InlineKeyboardButton(f"{category}", callback_data=f'view_category_{category}')])
        keyboard.append([
            InlineKeyboardButton("ویرایش", callback_data=f'edit_category_{category}'),
            InlineKeyboardButton("حذف", callback_data=f'delete_category_{category}')
        ])

    # اضافه کردن دکمه بازگشت به منوی اصلی
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "مدیریت دسته‌بندی‌ها"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def add_category(update, context):
    """درخواست نام دسته‌بندی جدید از کاربر."""
    if update.callback_query:
        # حذف کیبورد شیشه‌ای قبلی
        # update.callback_query.edit_message_reply_markup(reply_markup=None)

        update.callback_query.message.reply_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data['adding_category'] = True
        update.callback_query.answer()

#pass
def handle_new_category(update, context):
    """افزودن دسته‌بندی جدید."""
    if context.user_data.get('adding_category'):
        new_category = update.message.text.strip()
        data = load_data()

        if 'categories' not in data:
            data['categories'] = []

        if new_category not in data['categories']:
            data['categories'].append(new_category)
            save_data(data)

            confirmation_message = update.message.reply_text(f"دسته‌بندی '{new_category}' با موفقیت اضافه شد.")

            # حذف پیام تایید و پیام درخواست نام دسته‌بندی
            # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
            # update.message.delete()

            # آپدیت منوی دسته‌بندی‌ها
            manage_categories(update, context)
        else:
            update.message.reply_text(f"دسته‌بندی '{new_category}' قبلاً وجود دارد.")
            manage_categories(update, context)

        context.user_data['adding_category'] = False
    else:
        update.message.reply_text("ابتدا از منوی مدیریت دسته‌بندی‌ها اقدام کنید.")
        manage_categories(update, context)

#pass
def edit_category(update, context):
    """درخواست نام جدید دسته‌بندی برای ویرایش."""
    query = update.callback_query
    category = query.data.split('_')[-1]

    # حذف کیبورد شیشه‌ای قبلی
    #query.edit_message_reply_markup(reply_markup=None)

    # ارسال پیام درخواست نام جدید دسته‌بندی
    query.message.reply_text(f"نام جدید دسته‌بندی '{category}' را وارد کنید:")
    context.user_data['editing_category'] = category
    query.answer()

#pass
def handle_edit_message(update, context):
    """ویرایش نام دسته‌بندی."""
    if 'editing_category' in context.user_data:
        old_category = context.user_data['editing_category']
        new_category = update.message.text.strip()
        data = load_data()

        if new_category in data.get("categories", []):
            update.message.reply_text("این دسته‌بندی قبلاً وجود دارد.")
        else:
            data['categories'].remove(old_category)
            data['categories'].append(new_category)
            save_data(data)

            confirmation_message = update.message.reply_text(f"دسته‌بندی '{old_category}' به '{new_category}' تغییر یافت.")

            # حذف پیام تایید و پیام درخواست نام جدید
            # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
            # update.message.delete()

            # آپدیت منوی دسته‌بندی‌ها
            manage_categories(update, context)

        context.user_data.clear()

#pass
def delete_category(update, context):
    """حذف دسته‌بندی."""
    query = update.callback_query
    category = query.data.split('_')[-1]
    data = load_data()

    if category in data.get("categories", []):
        data['categories'].remove(category)
        save_data(data)

        confirmation_message = query.message.reply_text(f"دسته‌بندی '{category}' حذف شد.")

        #  حذف پیام تایید و پیام قبلی و منوی شیشه ای قدیمی
        # (بلد نیستم)

        # آپدیت منوی دسته‌بندی‌ها
        manage_categories(update, context)
        # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
    else:
        query.message.reply_text("دسته‌بندی وجود ندارد.")
        manage_categories(update, context)

    query.answer()

#pass
def list_agents(update, context):
    """لیست نماینده‌ها و محصولات آن‌ها را به صورت پیام‌های جداگانه با دکمه‌های شیشه‌ای نمایش می‌دهد."""
    data = load_data()
    agents = data.get("agents", {})
    
    if agents:
        for agent_id, agent_info in agents.items():
            agent = data["users"].get(agent_id)
            if agent and agent.get('role') == 'agent':
                agent_name = agent.get('name', 'بدون نام')
                product_ids = agent_info.get('products', [])
                product_count = len(product_ids)
                
                # دکمه اصلی نماینده شامل نام و تعداد محصولات
                keyboard = [
                    # دکمه مدیریت نماینده
                    [InlineKeyboardButton(f"مدیریت نماینده", callback_data=f'manage_agent_{agent_id}')],
                    # دکمه نمایش تعداد محصولات
                    [InlineKeyboardButton(f"↓↓ تعداد محصولات: {product_count} ↓↓", callback_data=f'view_agent_{agent_id}')]
                ]

                # دکمه‌ها برای هر محصول نماینده
                if product_count > 0:
                    for product_id in product_ids:
                        product_info = data["products"].get(str(product_id))
                        if product_info:
                            product_name = product_info.get('name', 'بدون نام')

                            # دکمه برای هر محصول
                            keyboard.append([InlineKeyboardButton(f"📦 {product_name}", callback_data=f'admin_manage_single_product_{agent_id}_{product_id}')])
                            # دکمه‌های ویرایش و حذف برای هر محصول
                            """keyboard.append([
                                InlineKeyboardButton("ویرایش", callback_data=f'edit_product_{product_id}'),
                                InlineKeyboardButton("حذف", callback_data=f'delete_product_{product_id}')
                            ])"""
                else:
                    keyboard.append([InlineKeyboardButton("این نماینده هنوز هیچ محصولی اضافه نکرده است.", callback_data='no_action')])

                # دکمه بازگشت به منوی اصلی برای هر نماینده
                keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='admin_menu')])

                # تنظیمات کیبورد
                reply_markup = InlineKeyboardMarkup(keyboard)

                # پیام مربوط به هر نماینده
                message = f"👤 نماینده: {agent_name} (ID: {agent_id})"
                
                # ارسال پیام جداگانه برای هر نماینده
                if update.callback_query:
                    update.callback_query.message.delete()  # حذف پیام قبلی
                    update.callback_query.message.reply_text(message, reply_markup=reply_markup)
                    update.callback_query.answer()
                else:
                    update.message.reply_text(message, reply_markup=reply_markup)
    else:
        if update.message:
            update.message.reply_text("هیچ نماینده‌ای وجود ندارد.")
        elif update.callback_query:
            update.callback_query.message.reply_text("هیچ نماینده‌ای وجود ندارد.")
            update.callback_query.answer()

#pass
def manage_agent(update, context):
    """مدیریت اطلاعات نماینده شامل حذف و دریافت گزارش."""
    query = update.callback_query
    data = query.data  # دریافت داده callback_query
    agent_id = data.split('_')[-1]  # استخراج agent_id از callback_data
    
    # بارگذاری داده‌ها
    data = load_data()
    agent = data["users"].get(agent_id)

    if agent:
        agent_name = agent.get('name', 'بدون نام')

        # ساختار دکمه‌های مدیریتی
        keyboard = [
            [InlineKeyboardButton("دریافت گزارش کامل", callback_data=f'get_report_{agent_id}')],
            [InlineKeyboardButton("حذف نماینده", callback_data=f'delete_agent_{agent_id}')],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='admin_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"مدیریت نماینده {agent_name} (ID: {agent_id})"
        
        # ارسال پیام مدیریت نماینده
        query.message.reply_text(message, reply_markup=reply_markup)
        query.answer()
    else:
        query.message.reply_text("نماینده موردنظر یافت نشد.")
        query.answer()

#pass
def get_report(update, context):
    """Generate a report for a specific agent including sold products and total sales value."""
    query = update.callback_query
    data = query.data  # دریافت داده callback_query
    agent_id = data.split('_')[-1]  # استخراج agent_id از callback_data

    # بارگذاری داده‌ها
    data = load_data()
    agent = data["users"].get(agent_id)
    products = data.get("products", {})

    if not agent:
        query.message.reply_text("نماینده موردنظر یافت نشد.")
        query.answer()
        return

    agent_name = agent.get('name', 'بدون نام')
    total_sales_value = 0
    sold_products_report = ""

    # بررسی محصولات نماینده و جمع آوری اطلاعات فروش
    for product_id in agent.get('products', []):
        product_info = products.get(str(product_id))

        if product_info:
            product_name = product_info.get('name', 'نامشخص')
            product_price = product_info.get('price', 0)
            sold_quantity = product_info.get('sold', 0)

            # فقط محصولاتی که فروش داشته‌اند
            if sold_quantity > 0:
                # محاسبه مبلغ فروش
                sales_value = product_price * sold_quantity
                total_sales_value += sales_value

                # جزئیات محصول را به گزارش اضافه کنید
                sold_products_report += (
                    f"نام محصول: {product_name}\n"
                    f"قیمت: {product_price if product_price else 'نامشخص'} تومان\n"
                    f"تعداد فروخته شده: {sold_quantity}\n"
                    f"مبلغ فروش: {sales_value} تومان\n"
                    "-----------------------------\n"
                )

    # ساخت پیام نهایی گزارش
    report_message = (
        f"گزارش نماینده: {agent_name}\n (ID: {agent_id})\n\n"
        f"مبلغ کل فروش: {total_sales_value} تومان\n"
        "-----------------------------\n"
        f"گزارش محصولات فروخته شده:\n"
        f"{sold_products_report if sold_products_report else 'محصول فروخته شده‌ای وجود ندارد.'}\n"
    )

    # ارسال گزارش به نماینده
    query.message.reply_text(report_message)
    query.answer()

#pass
def delete_agent(update, context):
    """حذف نماینده از لیست و بروزرسانی داده‌ها."""
    query = update.callback_query
    data = query.data  # دریافت داده‌های callback
    agent_id = data.split('_')[-1]  # استخراج agent_id از callback_data

    # بارگذاری داده‌ها از فایل JSON
    data = load_data()

    # بررسی وجود نماینده
    agent = data["users"].get(agent_id)
    
    if agent and agent.get('role') == 'agent':
        # یافتن محصولات نماینده
        products_to_delete = data["agents"].get(agent_id, {}).get("products", [])
        
        # حذف محصولات از لیست محصولات
        for product_id in products_to_delete:
            if str(product_id) in data["products"]:
                del data["products"][str(product_id)]  # حذف محصول از دیکشنری محصولات

        # حذف نماینده از لیست کاربران
        del data["users"][agent_id]
        
        # حذف نماینده از لیست نمایندگان
        if agent_id in data["agents"]:
            del data["agents"][agent_id]

        save_data(data)  # ذخیره تغییرات به فایل JSON
        query.message.reply_text(f"نماینده '{agent.get('name', 'بدون نام')}' و محصولات مربوط به آن با موفقیت حذف شدند.")
    else:
        query.message.reply_text("نماینده موردنظر یافت نشد یا حذف شد.")

    query.answer()

#pass
def admin_manage_single_product(update, context):
    """نمایش اطلاعات یک محصول خاص و گزینه‌های مدیریت آن."""
    data = update.callback_query.data  # دریافت داده callback
    parts = data.split('_')  # تقسیم داده به اجزا
    if len(parts) < 3:
        update.callback_query.message.reply_text("داده‌های لازم برای مدیریت محصول کامل نیست.")
        update.callback_query.answer()
        return
    
    agent_id = parts[4]  # استخراج agent_id
    product_id = parts[5]  # استخراج product_id
    data = load_data()
    
    # یافتن محصول بر اساس شناسه محصول
    product_info = data["products"].get(str(product_id))
    agent = data["users"].get(agent_id)

    if product_info and agent:
        agent_name = agent.get('name', 'بدون نام')
        product_name = product_info.get('name', 'نام نامشخص')
        price = product_info.get('price', 'بدون قیمت')
        stock = product_info.get('stock', 'بدون موجودی')
        product_city = product_info.get('city', 'بدون شهر')
        category = product_info.get('category', 'بدون دسته‌بندی')

        # پیام محصول به همراه اطلاعات کامل
        product_message = (
            f"📦 نام محصول: {product_name}\n"
            f"قیمت: {price} تومان\n"
            f"شهر: {product_city}\n"
            f"موجودی: {stock}\n"
            f"نماینده: {agent_name}\n"
            f"دسته‌بندی: {category}\n"
        )

        # ایجاد دکمه‌های شیشه‌ای برای ویرایش و حذف
        keyboard = [
            [
                InlineKeyboardButton("ویرایش", callback_data=f"admin_edit_product_{agent_id}_{product_id}"),
                InlineKeyboardButton("حذف", callback_data=f"admin_delete_product_{product_id}")
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="list_agents")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # ارسال پیام محصول
        if update.callback_query:
            update.callback_query.message.delete()
            update.callback_query.message.reply_text(product_message, reply_markup=reply_markup)
            update.callback_query.answer()
    else:
        if update.callback_query:
            update.callback_query.message.reply_text("محصول موردنظر یافت نشد یا نماینده معتبر نیست.")
            update.callback_query.answer()

#pass
def admin_delete_product(update, context):
    """حذف محصول توسط ادمین."""
    query_data = update.callback_query.data.split('_')
    product_id = query_data[4]  # استخراج product_id

    data = load_data()
    product_info = data["products"].get(product_id)

    if product_info:
        agent_id = product_info['agent_id']  # استخراج agent_id از اطلاعات محصول
        agent_info = data["agents"].get(agent_id)

        # حذف محصول از لیست محصولات نماینده
        if agent_info and int(product_id) in agent_info['products']:  # تغییر این خط به int برای مطابقت با نوع داده
            agent_info['products'].remove(int(product_id))  # حذف شناسه محصول از لیست نماینده
            del data["products"][product_id]  # حذف محصول از دیتابیس
            save_data(data)  # ذخیره تغییرات در فایل

            update.callback_query.message.reply_text(f"محصول {product_info['name']} با موفقیت حذف شد.")
        else:
            update.callback_query.message.reply_text("محصول در لیست نماینده یافت نشد.")
    else:
        update.callback_query.message.reply_text("محصول یافت نشد.")

    update.callback_query.answer()

#soon
def admin_edit_product(update, context):
    """ویرایش محصول توسط ادمین."""
    update.callback_query.message.reply_text(f"این بخش در اپدیت بعدی اضافه خواهد شد")
    update.callback_query.answer()


def add_agent_start(update, context):
    """شروع فرآیند افزودن نماینده با درخواست ID عددی نماینده جدید."""
    print('test add agent')
    update.callback_query.message.reply_text("لطفاً ID عددی نماینده جدید را وارد کنید:")
    update.callback_query.answer()

    # ذخیره مرحله برای دریافت ID نماینده
    context.user_data['adding_agent'] = True

def add_agent(update, context):
    """افزودن نماینده جدید به دیتابیس."""
    if 'adding_agent' in context.user_data and context.user_data['adding_agent']:
        agent_id = update.message.text.strip()  # دریافت ID نماینده از ورودی کاربر

        # بررسی اینکه ID عددی است
        if agent_id.isdigit():
            agent_id = str(agent_id)  # تبدیل به رشته برای ذخیره در دیتابیس

            # بارگذاری داده‌ها از فایل
            data = load_data()

            # بررسی اینکه آیا نماینده با این ID قبلاً وجود دارد
            if agent_id not in data['users']:
                # افزودن نماینده به دیتابیس
                data['users'][agent_id] = {
                    "role": "agent",
                    "balance": 0,
                    "city": "",
                    "cart": {},
                    "orders": []
                }

                # همچنین نماینده را به لیست نمایندگان اضافه کنیم
                data['agents'][agent_id] = {
                    "products": []  # لیست محصولات نماینده در حال حاضر خالی است
                }

                # ذخیره‌سازی تغییرات
                save_data(data)

                update.message.reply_text(f"نماینده با ID {agent_id} با موفقیت اضافه شد.")
            else:
                update.message.reply_text("این ID نماینده قبلاً وجود دارد. لطفاً یک ID دیگر وارد کنید.")
        else:
            update.message.reply_text("لطفاً یک ID عددی معتبر وارد کنید.")
    else:
        update.message.reply_text("فرآیند افزودن نماینده هنوز آغاز نشده است.")


#pass
def admin_report(update, context):
    """Generate a report for admin including total users, agents, sold products, and total sales value."""
    data = load_data()  # Load data from JSON file

    # Calculate the number of users and agents
    users = data.get('users', {})
    agents = data.get('agents', {})
    total_users = len(users)
    total_agents = len(agents)

    # Report on sold products and total sales value
    products = data.get('products', {})
    total_sales_value = 0
    sold_products_report = ""

    for product_id, product_info in products.items():
        product_name = product_info.get('name', 'نامشخص')
        product_price = product_info.get('price', 0)
        sold_quantity = product_info.get('sold', 0)

        # Only include products with sold quantity greater than 0
        if sold_quantity > 0:
            # Ensure price is not None before calculation
            if product_price is not None:
                sales_value = product_price * sold_quantity
            else:
                sales_value = 0

            total_sales_value += sales_value

            # Append product sales details to the report
            sold_products_report += (
                f"نام محصول: {product_name}\n"
                f"قیمت: {product_price if product_price else 'نامشخص'} تومان\n"
                f"تعداد فروخته شده: {sold_quantity}\n"
                f"مبلغ فروش: {sales_value} تومان\n"
                "-----------------------------\n"
            )

    # Construct the final report message
    report_message = (
        f"📊 گزارش کل 📊\n\n"
        f"تعداد کاربران: {total_users}\n"
        f"تعداد نماینده‌ها: {total_agents}\n\n"
        f"مبلغ کل فروش: {total_sales_value} تومان\n"
        "-----------------------------\n"
        f"گزارش محصولات فروخته شده:\n"
        f"{sold_products_report if sold_products_report else 'محصول فروخته شده‌ای وجود ندارد.'}\n"
    )

    # Check if update.message is available
    if update.message:
        # Send the report to the admin
        update.message.reply_text(report_message)
    else:
        # Alternative way to send a message (for example, to the chat_id)
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text=report_message)


"""
check list:

- افزودن مدیریت دسته بندی 
(لیست دسته بندی ها) 
    افزودن دسته بندی 
    حذف 
    ویرایش 

- لیست نماینده ها 
(نماینده و جزییات) 
    افزودن نماینده 

- مدیریت محصولات


- گذارش گیری \\
(نمایش گذارش کامل)

"""