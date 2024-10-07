from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

PROVINCES_CITIES = {
    "آذربایجان شرقی": ["تبریز", "مراغه", "مرند", "اهر", "بناب", "میانه", "سراب", "شبستر", "بستان‌آباد", "ملکان"],
    "آذربایجان غربی": ["ارومیه", "خوی", "میاندوآب", "بوکان", "مهاباد", "سلماس", "پیرانشهر", "نقده", "شاهین‌دژ"],
    "اردبیل": ["اردبیل", "مشگین‌شهر", "پارس‌آباد", "خلخال", "بیله‌سوار", "گرمی", "نمین", "نیر", "کوثر"],
    "اصفهان": ["اصفهان", "کاشان", "خمینی‌شهر", "نجف‌آباد", "فلاورجان", "شاهین‌شهر", "گلپایگان", "لنجان", "مبارکه"],
    "البرز": ["کرج", "نظرآباد", "ساوجبلاغ", "فردیس", "طالقان", "اشتهارد", "هشتگرد"],
    "ایلام": ["ایلام", "دهلران", "ایوان", "دره‌شهر", "آبدانان", "مهران", "چرداول", "ملکشاهی", "بدره"],
    "بوشهر": ["بوشهر", "برازجان", "کنگان", "گناوه", "دشتی", "دیر", "دشتستان", "عسلویه", "تنگستان"],
    "تهران": ["تهران", "ورامین", "پیشوا", "شهریار", "اسلامشهر", "پاکدشت", "رباط‌کریم", "قدس", "بهارستان", "ملارد"],
    "چهارمحال و بختیاری": ["شهرکرد", "بروجن", "فارسان", "لردگان", "کوهرنگ", "اردل", "کیار", "سامان", "بن"],
    "خراسان جنوبی": ["بیرجند", "قائن", "طبس", "فردوس", "نهبندان", "سربیشه", "درمیان", "بشرویه", "خوسف"],
    "خراسان رضوی": ["مشهد", "نیشابور", "تربت‌حیدریه", "سبزوار", "قوچان", "کاشمر", "گناباد", "تایباد", "چناران"],
    "خراسان شمالی": ["بجنورد", "اسفراین", "شیروان", "آشخانه", "فاروج", "جاجرم", "گرمه", "مانه و سملقان"],
    "خوزستان": ["اهواز", "آبادان", "خرمشهر", "دزفول", "بهبهان", "ماهشهر", "شوش", "اندیمشک", "شادگان", "مسجدسلیمان"],
    "زنجان": ["زنجان", "ابهر", "خرمدره", "قیدار", "سلطانیه", "طارم", "ماهنشان"],
    "سمنان": ["سمنان", "شاهرود", "دامغان", "گرمسار", "مهدیشهر", "میامی", "سرخه", "آرادان"],
    "سیستان و بلوچستان": ["زاهدان", "چابهار", "زابل", "ایرانشهر", "سراوان", "خاش", "کنارک", "سرباز", "نیک‌شهر"],
    "فارس": ["شیراز", "مرودشت", "جهرم", "فسا", "کازرون", "داراب", "لارستان", "آباده", "فیروزآباد", "ممسنی"],
    "قزوین": ["قزوین", "البرز", "آبیک", "تاکستان", "بوئین‌زهرا", "اوج", "آوج"],
    "قم": ["قم"],
    "کردستان": ["سنندج", "سقز", "مریوان", "بانه", "قروه", "بیجار", "کامیاران", "دیواندره", "دهگلان"],
    "کرمان": ["کرمان", "رفسنجان", "جیرفت", "سیرجان", "زرند", "بم", "کهنوج", "عنبرآباد", "راور", "بافت"],
    "کرمانشاه": ["کرمانشاه", "اسلام‌آباد غرب", "هرسین", "کنگاور", "صحنه", "سنقر", "جوانرود", "سرپل‌ذهاب", "پاوه"],
    "کهگیلویه و بویراحمد": ["یاسوج", "دوگنبدان", "دهدشت", "سی‌سخت", "لیکک"],
    "گلستان": ["گرگان", "گنبدکاووس", "علی‌آباد کتول", "آق‌قلا", "بندرترکمن", "مینو‌دشت", "کردکوی", "کلاله", "گمیشان"],
    "گیلان": ["رشت", "انزلی", "لاهیجان", "لنگرود", "تالش", "آستارا", "رودبار", "فومن", "صومعه‌سرا"],
    "لرستان": ["خرم‌آباد", "بروجرد", "دورود", "الیگودرز", "نورآباد", "الشتر", "ازنا", "کوهدشت", "پلدختر"],
    "مازندران": ["ساری", "بابل", "آمل", "قائم‌شهر", "نوشهر", "چالوس", "تنکابن", "بابلسر", "جویبار", "بهشهر"],
    "مرکزی": ["اراک", "ساوه", "خمین", "محلات", "دلیجان", "تفرش", "آشتیان", "شازند", "خنداب"],
    "هرمزگان": ["بندرعباس", "قشم", "کیش", "میناب", "بندر لنگه", "جاسک", "بستک", "حاجی‌آباد", "خمیر"],
    "همدان": ["همدان", "ملایر", "نهاوند", "تویسرکان", "اسدآباد", "کبودرآهنگ", "رزن", "فامنین"],
    "یزد": ["یزد", "میبد", "اردکان", "تفت", "ابرکوه", "مهریز", "بافق", "اشکذر", "خاتم"]
}
#pass
def agent_menu(update, context):
    """Display the main agency menu."""
    keyboard = [
        [InlineKeyboardButton("افزودن محصول جدید", callback_data='agent_add_product')],
        [InlineKeyboardButton("لیست محصولات من", callback_data='agent_list_my_products')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "به پنل نمایندگی خوش آمدید"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def agent_add_product(update, context):
    """Request and process new product details from the agent."""
    
    # Initial start, request product name
    if 'adding_product' not in context.user_data:
        keyboard = [[InlineKeyboardButton("لغو", callback_data='agent_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "نام محصول را وارد کنید."
        context.user_data['adding_product'] = True

        if update.callback_query:
            update.callback_query.message.delete()  # حذف پیام قبلی
            update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            update.callback_query.answer()
        else:
            update.message.reply_text(message, reply_markup=reply_markup)
    
    # Step 1: Request product name
    elif 'product_name' not in context.user_data:
        context.user_data['product_name'] = update.message.text
        keyboard = [[InlineKeyboardButton("لغو", callback_data='agent_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("توضیحات محصول را وارد کنید.", reply_markup=reply_markup)
    
    # Step 2: Request product description
    elif 'product_description' not in context.user_data:
        context.user_data['product_description'] = update.message.text
        keyboard = [[InlineKeyboardButton("لغو", callback_data='agent_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("قیمت محصول را وارد کنید.", reply_markup=reply_markup)
    
    # Step 3: Request product price
    elif 'product_price' not in context.user_data:
        price_text = update.message.text
        if price_text.isdigit():  # Ensure price is a positive number
            context.user_data['product_price'] = int(price_text)
            keyboard = [[InlineKeyboardButton("لغو", callback_data='agent_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("موجودی محصول را وارد کنید.", reply_markup=reply_markup)
        else:
            update.message.reply_text("لطفاً یک قیمت معتبر وارد کنید.")  # Error for invalid price
    
    # Step 4: Request product stock
    elif 'product_stock' not in context.user_data:
        stock_text = update.message.text
        if stock_text.isdigit():  # Ensure stock is a positive number
            context.user_data['product_stock'] = int(stock_text)
            agent_show_provinces(update, context)  # نمایش لیست استان‌ها
        else:
            update.message.reply_text("لطفاً یک عدد معتبر برای موجودی وارد کنید.")  # Error for invalid stock
    
    # Step 5: Province and city selection (handled by agent_show_provinces/agent_show_cities)
    elif 'current_city' in context.user_data:
        agent_save_new_product(update, context)  # Save the product after selecting city

#pass
def agent_show_provinces(update, context):
    """Display the list of provinces for selection."""
    keyboard = [[InlineKeyboardButton(province, callback_data=f"agent_province_{province}")] for province in PROVINCES_CITIES.keys()]
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='agent_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً استان خود را انتخاب کنید:"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def agent_handle_province_selection(update, context):
    """Manage the province selection by the agent."""
    try:
        province = update.callback_query.data.split('_')[2]
        if province in PROVINCES_CITIES:
            context.user_data['current_province'] = province
            agent_show_cities(update, context, province)
        else:
            print(province)
            update.callback_query.message.reply_text("استان انتخاب‌شده معتبر نیست.")
    except IndexError:
        print(province)
        update.callback_query.message.reply_text("مشکلی در انتخاب استان به وجود آمد.")
    update.callback_query.answer()

#pass
def agent_show_cities(update, context, province):
    """Display the cities of the selected province."""
    if province in PROVINCES_CITIES:
        cities = PROVINCES_CITIES[province]
        keyboard = [[InlineKeyboardButton(city, callback_data=f"agent_city_{city}")] for city in cities]
        keyboard.append([InlineKeyboardButton("بازگشت", callback_data='agent_show_provinces')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"لطفاً یکی از شهرهای استان {province} را انتخاب کنید:"
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
    else:
        print(province)
        update.callback_query.message.reply_text("استان انتخاب‌شده معتبر نیست.")
    update.callback_query.message.delete()
    update.callback_query.answer()

#pass
def agent_handle_city_selection(update, context):
    """Manage the city selection by the agent and direct to category selection."""
    city = update.callback_query.data.split('_')[1]
    context.user_data['current_city'] = city
    agent_show_categories(update, context)
    update.callback_query.answer()

#pass
def agent_handle_category_selection(update, context):
    """Manage the category selection by the agent and save it."""
    category = update.callback_query.data.split('_')[1]
    context.user_data['product_category'] = category
    # Now that we have all the product information, save the product
    agent_save_new_product(update, context)
    update.callback_query.answer()

#pass
def agent_save_new_product(update, context):
    """Save the new product in the database."""
    data = load_data()

    # Get product information from context.user_data
    product_name = context.user_data.get('product_name')
    product_description = context.user_data.get('product_description')
    product_price = context.user_data.get('product_price')
    product_stock = context.user_data.get('product_stock')
    product_category = context.user_data.get('product_category')
    city = context.user_data.get('current_city')
    province = context.user_data.get('current_province')
    agent_id = str(update.effective_user.id)

    # Find the first available product ID from 1 to inf
    product_id = agent_find_next_product_id(data)

    # Create a new entry for the product in the 'products' section
    if 'products' not in data:
        data['products'] = {}
    data['products'][product_id] = {
        'name': product_name,
        'description': product_description,
        'price': product_price,
        'stock': product_stock,
        'sold': 0,  # Number sold (initially 0)
        'category': product_category,
        'province': province,
        'city': city,
        'agent_id': agent_id
    }

    # Ensure the 'agents' section exists and add the product ID to it
    if 'agents' not in data:
        data['agents'] = {}
    if agent_id not in data['agents']:
        data['agents'][agent_id] = {'products': []}

    # Add the product ID to the agent's product list in the 'agents' section
    data['agents'][agent_id]['products'].append(product_id)
    save_data(data)

    # Send a confirmation message to the agent
    product_details = (
        f"محصول شما با موفقیت اضافه شد:\n"
        f"نام: {data['products'][product_id]['name']}\n"
        f"توضیحات: {data['products'][product_id]['description']}\n"
        f"قیمت: {data['products'][product_id]['price']} تومان\n"
        f"موجودی: {data['products'][product_id]['stock']} عدد\n"
        f"دسته‌بندی: {data['products'][product_id]['category']}\n"
        f"شهر: {data['products'][product_id]['city']}\n"
    )
    update.callback_query.message.reply_text(product_details)
    update.callback_query.message.delete()
    context.user_data.clear()
    agent_menu(update, context)

#pass
def agent_find_next_product_id(data):
    """Find the first available product ID."""
    used_product_ids = set(map(int, data.get('products', {}).keys()))
    product_id = 1
    while product_id in used_product_ids:
        product_id += 1
    return product_id

#pass
def agent_show_categories(update, context):
    """Display the available categories as inline buttons."""
    data = load_data()
    categories = data.get('categories', [])

    # Create inline buttons for each category
    keyboard = [[InlineKeyboardButton(category, callback_data=f"agent_category_{category}")] for category in categories]
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='agent_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً یک دسته‌بندی برای محصول انتخاب کنید:"

    if update.callback_query:
        update.callback_query.message.delete()  # حذف پیام قبلی
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)


def agent_list_my_products(update, context):
    """Display agent's products with options to edit or delete."""
    
    agent_id = update.effective_user.id  # Assuming agent ID is same as Telegram user ID
    agent_products = get_agent_products(agent_id)  # فانکشن کمکی که محصولات نماینده را از دیتابیس بگیرد

    if not agent_products:
        update.message.reply_text("شما هیچ محصولی ثبت نشده ندارید.")
        return

    keyboard = []
    for product in agent_products:
        product_id = product['product_id']
        product_name = product['name']
        
        # دکمه برای نمایش هر محصول با گزینه‌های ویرایش و حذف
        keyboard.append([InlineKeyboardButton(f"{product_name}", callback_data=f"product_{product_id}")])
        keyboard.append([
            InlineKeyboardButton("🖋️ ویرایش", callback_data=f"edit_product_{product_id}"),
            InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_product_{product_id}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("لیست محصولات شما:", reply_markup=reply_markup)

def agent_edit_product(update, context):
    """Handle editing options for a specific product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]
    
    keyboard = [
        [InlineKeyboardButton("🖋️ ویرایش اسم", callback_data=f"edit_name_{product_id}")],
        [InlineKeyboardButton("🖋️ ویرایش توضیحات", callback_data=f"edit_description_{product_id}")],
        [InlineKeyboardButton("🖋️ ویرایش قیمت", callback_data=f"edit_price_{product_id}")],
        [InlineKeyboardButton("🖋️ ویرایش موجودی", callback_data=f"edit_stock_{product_id}")],
        [InlineKeyboardButton("🖋️ ویرایش استان و شهر", callback_data=f"edit_location_{product_id}")],
        [InlineKeyboardButton("🖋️ ویرایش دسته‌بندی", callback_data=f"edit_category_{product_id}")],
        [InlineKeyboardButton("لغو", callback_data="agent_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"ویرایش محصول {product_id}:", reply_markup=reply_markup)

def agent_delete_product(update, context):
    """Handle product deletion confirmation."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]
    
    # حذف محصول از دیتابیس (json)
    delete_product_from_database(product_id)  # فانکشن کمکی برای حذف محصول
    
    query.edit_message_text(f"محصول {product_id} با موفقیت حذف شد.")







"""
check list:
- مدیریت محصولات
افزودن محصول جدید \\
    انتخاب نام \\
    انتخاب توضیحات \\
    انتخاب قیمت \\
    انتخاب موجودی \\
    انتخاب استان \\
    انتخاب شهر \\
    انتخاب دسته بندی \\

لیست محصولات من
(نمایش محصولات در دکمه شیشه ای همراه دکمه های حذف و ادیت)
    ادیت محصول
            ادیت اسم
                نوشتن اسم جدید
            ادیت توضیحات
                نوشتن توضیحات جدید
            ادیت قیمت
                نوشتن قیمت جدید
            ادیت موجودی
                نوشتن موجودی جدید
            ادیت استان و شهر
                انتخاب استان جدید   
                انتخاب شهر جدید         
            ادیت دسته بندی
                انتخاب دسته بندی جدید
    حذف محصول
        فرایند حذف محصول از همه بخش های فایل json
"""