from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

def admin_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("مدیریت دسته‌بندی‌ها", callback_data='manage_categories')],
        [InlineKeyboardButton("لیست نماینده‌ها", callback_data='list_agents')],
        [InlineKeyboardButton("مدیریت محصولات", callback_data='manage_products')],
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
    data = load_data()
    categories = data.get("categories", {})
    
    # دکمه افزودن دسته‌بندی ایجاد می‌شود
    keyboard = [[InlineKeyboardButton("افزودن دسته‌بندی", callback_data='add_category')]]

    # برای هر دسته‌بندی، دکمه‌های نام، ویرایش و حذف ایجاد می‌شود
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
    # درخواست نام دسته‌بندی جدید از کاربر
    if update.callback_query:
        update.callback_query.message.reply_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data['adding_category'] = True  # فعال کردن حالت افزودن دسته‌بندی
        update.callback_query.answer()

def handle_new_category(update, context):
    # این تابع زمانی فراخوانی می‌شود که کاربر نام دسته‌بندی جدید را وارد کند
    if context.user_data.get('adding_category'):
        new_category = update.message.text.strip()  # دریافت نام دسته‌بندی جدید
        data = load_data()  # بارگذاری داده‌ها از فایل JSON

        if 'categories' not in data:
            data['categories'] = []

        # بررسی اینکه دسته‌بندی وجود نداشته باشد
        if new_category not in data['categories']:
            data['categories'].append(new_category)
            save_data(data)  # ذخیره دسته‌بندی جدید
            update.message.reply_text(f"دسته‌بندی '{new_category}' با موفقیت اضافه شد.")
        else:
            update.message.reply_text(f"دسته‌بندی '{new_category}' قبلاً وجود دارد.")

        context.user_data['adding_category'] = False  # غیرفعال کردن حالت افزودن
    else:
        update.message.reply_text("ابتدا از منوی مدیریت دسته‌بندی‌ها اقدام کنید.")

def edit_category(update, context):
    # دریافت دسته‌بندی برای ویرایش
    query = update.callback_query
    category = query.data.split('_')[-1]  # استخراج نام دسته‌بندی از callback_data
    query.message.reply_text(f"نام جدید دسته‌بندی '{category}' را وارد کنید:")
    context.user_data['editing_category'] = category
    query.answer()

def handle_edit_message(update, context):
    # ویرایش نام دسته‌بندی
    if 'editing_category' in context.user_data:
        old_category = context.user_data['editing_category']
        new_category = update.message.text.strip()
        data = load_data()
        categories = data.get("categories", {})

        if new_category in categories:
            update.message.reply_text("این دسته‌بندی قبلاً وجود دارد.")
        else:
            categories[new_category] = categories.pop(old_category)  # تغییر نام دسته‌بندی
            save_data(data)
            update.message.reply_text(f"دسته‌بندی '{old_category}' به '{new_category}' تغییر یافت.")

        context.user_data.clear()  # پاک کردن وضعیت کاربر

def delete_category(update, context):
    # حذف دسته‌بندی
    query = update.callback_query
    category = query.data.split('_')[-1]  # استخراج نام دسته‌بندی از callback_data
    data = load_data()
    categories = data.get("categories", {})

    if category in categories:
        del categories[category]
        save_data(data)  # ذخیره تغییرات
        query.message.reply_text(f"دسته‌بندی '{category}' حذف شد.")
    else:
        query.message.reply_text("دسته‌بندی وجود ندارد.")
    
    query.answer()

def list_agents(update, context):
    data = load_data()
    agents = data.get("agents", {})
    message = "لیست نماینده‌ها:\n"
    
    for city, agent_info in agents.items():
        agent = data["users"].get(str(agent_info["agent_id"]))
        message += f"{city}: {agent['name']} - محصولات: {len(agent_info['products'])}\n"

    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()
