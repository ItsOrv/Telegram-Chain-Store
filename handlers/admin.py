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
    keyboard = [[InlineKeyboardButton("افزودن دسته‌بندی", callback_data='add_category')]]

    for category in categories:
        keyboard.append([
            InlineKeyboardButton(f"ویرایش {category}", callback_data=f'edit_category_{category}'),
            InlineKeyboardButton(f"حذف {category}", callback_data=f'delete_category_{category}')
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "دسته‌بندی‌های موجود:\n" + "\n".join(categories) if categories else "هیچ دسته‌بندی وجود ندارد."
    
    if update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def add_category(update, context):
    if update.callback_query:
        update.callback_query.message.reply_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data['adding_category'] = True
        update.callback_query.answer()

def handle_message(update, context):
    if context.user_data.get('adding_category'):
        new_category = update.message.text.strip()
        data = load_data()
        categories = data.get("categories", {})

        if new_category in categories:
            update.message.reply_text("این دسته‌بندی قبلاً وجود دارد.")
        else:
            categories[new_category] = []  # می‌توانید به هر دسته بندی محصولات مرتبط اضافه کنید
            data["categories"] = categories
            save_data(data)
            update.message.reply_text(f"دسته‌بندی '{new_category}' با موفقیت اضافه شد.")
        
        context.user_data.clear()

def edit_category(update, context, category):
    if update.callback_query:
        update.callback_query.message.reply_text(f"نام جدید دسته‌بندی '{category}' را وارد کنید:")
        context.user_data['editing_category'] = category
        update.callback_query.answer()

def handle_edit_message(update, context):
    if 'editing_category' in context.user_data:
        old_category = context.user_data['editing_category']
        new_category = update.message.text.strip()
        data = load_data()
        categories = data.get("categories", {})

        if new_category in categories:
            update.message.reply_text("این دسته‌بندی قبلاً وجود دارد.")
        else:
            categories[new_category] = categories.pop(old_category)
            data["categories"] = categories
            save_data(data)
            update.message.reply_text(f"دسته‌بندی '{old_category}' به '{new_category}' با موفقیت ویرایش شد.")
        
        context.user_data.clear()

def delete_category(update, context, category):
    if update.callback_query:
        data = load_data()
        categories = data.get("categories", {})
        
        if category in categories:
            del categories[category]
            data["categories"] = categories
            save_data(data)
            update.callback_query.message.reply_text(f"دسته‌بندی '{category}' با موفقیت حذف شد.")
        else:
            update.callback_query.message.reply_text("دسته‌بندی مورد نظر وجود ندارد.")

        update.callback_query.answer()

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
