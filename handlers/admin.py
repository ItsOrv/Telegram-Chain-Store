from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

def admin_menu(update, context):
    """نمایش منوی اصلی ادمین."""
    keyboard = [
        [InlineKeyboardButton("مدیریت دسته‌بندی‌ها", callback_data='manage_categories')],
        [InlineKeyboardButton("لیست نماینده‌ها", callback_data='list_agents')],
        [InlineKeyboardButton("مدیریت محصولات", callback_data='admin_manage_products')],
        [InlineKeyboardButton("گزارش‌گیری", callback_data='reports')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "به پنل ادمین خوش آمدید"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

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

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "مدیریت دسته‌بندی‌ها"

    if update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def add_category(update, context):
    """درخواست نام دسته‌بندی جدید از کاربر."""
    if update.callback_query:
        update.callback_query.message.reply_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data['adding_category'] = True
        update.callback_query.answer()

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
            update.message.reply_text(f"دسته‌بندی '{new_category}' با موفقیت اضافه شد.")
        else:
            update.message.reply_text(f"دسته‌بندی '{new_category}' قبلاً وجود دارد.")

        context.user_data['adding_category'] = False
    else:
        update.message.reply_text("ابتدا از منوی مدیریت دسته‌بندی‌ها اقدام کنید.")

def edit_category(update, context):
    """درخواست نام جدید دسته‌بندی برای ویرایش."""
    query = update.callback_query
    category = query.data.split('_')[-1]
    query.message.reply_text(f"نام جدید دسته‌بندی '{category}' را وارد کنید:")
    context.user_data['editing_category'] = category
    query.answer()

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
            update.message.reply_text(f"دسته‌بندی '{old_category}' به '{new_category}' تغییر یافت.")

        context.user_data.clear()

def delete_category(update, context):
    """حذف دسته‌بندی."""
    query = update.callback_query
    category = query.data.split('_')[-1]
    data = load_data()

    if category in data.get("categories", []):
        data['categories'].remove(category)
        save_data(data)
        query.message.reply_text(f"دسته‌بندی '{category}' حذف شد.")
    else:
        query.message.reply_text("دسته‌بندی وجود ندارد.")

    query.answer()

def list_agents(update, context):
    """لیست نماینده‌ها و محصولات آن‌ها را نمایش می‌دهد، هر محصول دارای شهر مجزا است."""
    data = load_data()
    agents = data.get("agents", {})
    message = "لیست نماینده‌ها و محصولات آن‌ها:\n\n"

    if agents:
        for city, agent_info in agents.items():
            agent_id = str(agent_info["agent_id"])
            agent = data["users"].get(agent_id)

            if agent:
                agent_name = agent.get('name', 'بدون نام')
                products = agent_info.get('products', {})
                product_count = len(products)

                # نمایش اطلاعات کلی نماینده
                message += f"📍 شهر نماینده: {city}\n"
                message += f"👤 نماینده: {agent_name} - تعداد محصولات: {product_count}\n"

                if product_count > 0:
                    message += "📦 محصولات:\n"
                    for product_name, product_info in products.items():
                        price = product_info.get('price', 'بدون قیمت')
                        stock = product_info.get('stock', 'بدون موجودی')
                        product_city = product_info.get('location', {}).get('city', 'بدون شهر')  # شهر محصول
                        
                        message += (
                            f"    🔹 {product_name}: قیمت {price} تومان - "
                            f"موجودی: {stock} - شهر: {product_city}\n"
                        )
                else:
                    message += "    ⚠️ این نماینده هنوز هیچ محصولی اضافه نکرده است.\n"
            else:
                message += f"⚠️ نماینده با ID {agent_id} یافت نشد.\n"
    else:
        message = "هیچ نماینده‌ای وجود ندارد."

    # ارسال پیام به کاربر
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()

    # اضافه کردن دکمه افزودن نماینده
    keyboard = [
        [InlineKeyboardButton("افزودن نماینده جدید", callback_data='add_agent')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def add_agent_start(update, context):
    """شروع فرآیند افزودن نماینده با درخواست ID عددی نماینده جدید."""
    print('test add agent')
    update.callback_query.message.reply_text("لطفاً ID عددی نماینده جدید را وارد کنید:")
    update.callback_query.answer()

    # ذخیره مرحله برای دریافت ID نماینده
    context.user_data['adding_agent'] = True

def list_agents(update, context):
    """لیست نماینده‌ها و محصولات آن‌ها را نمایش می‌دهد، هر محصول دارای شهر مجزا است."""
    data = load_data()
    agents = data.get("agents", {})
    message = "لیست نماینده‌ها و محصولات آن‌ها:\n\n"

    if agents:
        for agent_id, agent_info in agents.items():
            agent = data["users"].get(agent_id)
            if agent and agent.get('role') == 'agent':
                agent_name = agent.get('name', 'بدون نام')
                product_ids = agent_info.get('products', [])
                product_count = len(product_ids)

                # نمایش اطلاعات کلی نماینده
                message += f"👤 نماینده: {agent_name} (ID: {agent_id}) - تعداد محصولات: {product_count}\n"

                if product_count > 0:
                    message += "📦 محصولات:\n"
                    for product_id in product_ids:
                        product_info = data["products"].get(str(product_id))
                        if product_info:
                            product_name = product_info.get('name', 'بدون نام')
                            price = product_info.get('price', 'بدون قیمت')
                            stock = product_info.get('stock', 'بدون موجودی')
                            product_city = product_info.get('city', 'بدون شهر')
                            category = product_info.get('category', 'بدون دسته‌بندی')
                            
                            message += (
                                f"    🔹 {product_name}: قیمت {price} تومان - "
                                f"موجودی: {stock} - شهر: {product_city} - دسته‌بندی: {category}\n"
                            )
                        else:
                            message += f"    ⚠️ محصول با شناسه {product_id} یافت نشد.\n"
                else:
                    message += "    ⚠️ این نماینده هنوز هیچ محصولی اضافه نکرده است.\n"
            else:
                message += f"⚠️ نماینده با ID {agent_id} یافت نشد.\n"
    else:
        message = "هیچ نماینده‌ای وجود ندارد."

    # ارسال پیام به کاربر
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()

    # اضافه کردن دکمه افزودن نماینده
    keyboard = [
        [InlineKeyboardButton("افزودن نماینده جدید", callback_data='add_agent')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()



# admin prodict shits

def admin_manage_products(update, context):
    print("test admin product manage")
    """نمایش لیست محصولات برای مدیریت توسط ادمین."""
    data = load_data()
    agents = data.get("agents", {})
    message = "🔧 مدیریت محصولات:\n\n"

    if agents:
        for city, agent_info in agents.items():
            agent_id = str(agent_info["agent_id"])
            agent = data["users"].get(agent_id)

            if agent:
                agent_name = agent.get('name', 'بدون نام')
                products = agent_info.get('products', {})

                if products:
                    for product_name, product_info in products.items():
                        price = product_info.get('price', 'بدون قیمت')
                        stock = product_info.get('stock', 'بدون موجودی')
                        product_city = product_info.get('location', {}).get('city', 'بدون شهر')

                        # پیام محصول به همراه اطلاعات کامل
                        product_message = (
                            f"📦 نام محصول: {product_name}\n"
                            f"💰 قیمت: {price} تومان\n"
                            f"📍 شهر: {product_city}\n"
                            f"🔢 موجودی: {stock}\n"
                            f"👤 نماینده: {agent_name} (شهر نماینده: {city})\n"
                        )

                        # ایجاد دکمه‌های شیشه‌ای برای حذف و ویرایش
                        keyboard = [
                            [
                                InlineKeyboardButton("✏️ ویرایش", callback_data=f"admin_edit_product_{agent_id}_{product_name}"),
                                InlineKeyboardButton("❌ حذف", callback_data=f"admin_delete_product_{agent_id}_{product_name}")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)

                        # ارسال پیام هر محصول
                        if update.message:
                            update.message.reply_text(product_message, reply_markup=reply_markup)
                        elif update.callback_query:
                            update.callback_query.message.reply_text(product_message, reply_markup=reply_markup)
                            update.callback_query.answer()
                else:
                    message += f"نماینده {agent_name} (شهر: {city}) هیچ محصولی ندارد.\n"
    else:
        message = "هیچ نماینده‌ای ثبت نشده است."

    if message.strip():  # در صورت وجود نماینده‌هایی که محصول ندارند
        if update.message:
            update.message.reply_text(message)
        elif update.callback_query:
            update.callback_query.message.reply_text(message)
            update.callback_query.answer()


def admin_delete_product(update, context):
    """حذف محصول توسط ادمین."""
    query_data = update.callback_query.data.split('_')
    agent_id = query_data[3]
    product_name = '_'.join(query_data[4:])  # در صورتی که نام محصول شامل چند کلمه باشد

    data = load_data()
    agent_info = data["agents"].get(agent_id)

    if agent_info and product_name in agent_info['products']:
        del agent_info['products'][product_name]  # حذف محصول
        save_data(data)
        update.callback_query.message.reply_text(f"محصول {product_name} با موفقیت حذف شد.")
    else:
        update.callback_query.message.reply_text("محصول یافت نشد.")

    update.callback_query.answer()


def admin_edit_product(update, context):
    """ویرایش محصول توسط ادمین."""
    query_data = update.callback_query.data.split('_')
    agent_id = query_data[3]
    product_name = '_'.join(query_data[4:])  # در صورتی که نام محصول شامل چند کلمه باشد

    context.user_data['editing_product'] = {
        'agent_id': agent_id,
        'product_name': product_name
    }

    update.callback_query.message.reply_text(f"برای ویرایش محصول {product_name}، اطلاعات جدید را وارد کنید.")
    update.callback_query.answer()


from utils.helpers import load_data

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

- افزودن مدیریت دسته بندی \\
(لیست دسته بندی ها) \\
افزودن دسته بندی \\
حذف \\
ویرایش \\

- لیست نماینده ها \\
(نماینده و جزییات) \\
افزودن نماینده \\

- مدیریت محصولات


- گذارش گیری \\
(نمایش گذارش کامل) \\

"""