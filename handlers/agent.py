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

def start_agent(update, context):
    """Start the agency panel and display the initial menu."""
    agent_menu(update, context)

def agent_menu(update, context):
    """Display the main agency menu."""
    keyboard = [
        [InlineKeyboardButton("افزودن محصول جدید", callback_data='add_product')],
        [InlineKeyboardButton("لیست محصولات من", callback_data='list_my_products')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "به پنل نمایندگی خوش آمدید"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def show_provinces(update, context):
    """Display the list of provinces for selection."""
    keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in PROVINCES_CITIES.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً استان خود را انتخاب کنید:"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def show_cities(update, context, province):
    """Display the cities of the selected province."""
    cities = PROVINCES_CITIES[province]
    keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"لطفاً یکی از شهرهای استان {province} را انتخاب کنید:"
    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def handle_province_selection(update, context):
    """Manage the province selection by the agent."""
    province = update.callback_query.data.split('_')[1]
    context.user_data['current_province'] = province
    show_cities(update, context, province)

def find_next_product_id(data):
    """Find the first available product ID."""
    used_product_ids = set(map(int, data.get('products', {}).keys()))
    product_id = 1
    while product_id in used_product_ids:
        product_id += 1
    return product_id

def handle_city_selection(update, context):
    """Manage the city selection by the agent and direct to category selection."""
    city = update.callback_query.data.split('_')[1]
    context.user_data['current_city'] = city
    show_categories(update, context)
    update.callback_query.answer()

def handle_category_selection(update, context):
    """Manage the category selection by the agent and save it."""
    category = update.callback_query.data.split('_')[1]
    context.user_data['product_category'] = category
    # Now that we have all the product information, save the product
    save_new_product(update, context)
    update.callback_query.answer()

def add_product(update, context):
    """Request new product details from the agent."""
    if update.callback_query:
        update.callback_query.message.reply_text("نام محصول را وارد کنید.")
        update.callback_query.answer()
        context.user_data['adding_product'] = True

def handle_message(update, context):
    """Manage user messages for adding a product."""
    if context.user_data.get('adding_product'):
        process_product_details(update, context)

def process_product_details(update, context):
    """Process and save the details of the new product."""
    if 'product_name' not in context.user_data:
        context.user_data['product_name'] = update.message.text
        update.message.reply_text("توضیحات محصول را وارد کنید.")
    elif 'product_description' not in context.user_data:
        context.user_data['product_description'] = update.message.text
        update.message.reply_text("قیمت محصول را وارد کنید.")
    elif 'product_price' not in context.user_data:
        price_text = update.message.text
        if price_text.isdigit():
            context.user_data['product_price'] = int(price_text)
            update.message.reply_text("موجودی محصول را وارد کنید.")
        else:
            update.message.reply_text("لطفاً یک قیمت معتبر وارد کنید.")
    elif 'product_stock' not in context.user_data:
        stock_text = update.message.text
        if stock_text.isdigit():
            context.user_data['product_stock'] = int(stock_text)
            show_provinces(update, context)
        else:
            update.message.reply_text("لطفاً یک عدد معتبر برای موجودی وارد کنید.")
    elif 'current_city' in context.user_data:
        save_new_product(update, context)

def save_new_product(update, context):
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
    product_id = find_next_product_id(data)

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
    context.user_data.clear()

def show_categories(update, context):
    """Display the available categories as inline buttons."""
    data = load_data()
    categories = data.get('categories', [])

    # Create inline buttons for each category
    keyboard = [[InlineKeyboardButton(category, callback_data=f"category_{category}")] for category in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً یک دسته‌بندی برای محصول انتخاب کنید:"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def list_my_products(update, context):
    """Display the list of the agent's products."""
    city = context.user_data.get("current_city")
    data = load_data()
    products = data.get("agents", {}).get(city, {}).get("products", {})

    if products:
        message = "محصولات شما:\n"
        for product_name, product_info in products.items():
            message += f"{product_name} - قیمت: {product_info['price']} - موجودی: {product_info['stock']}\n"
    else:
        message = "شما هیچ محصولی ندارید."

    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()






#handle_new_product = handle_message
