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
    """شروع پنل نمایندگی و نمایش منوی اولیه."""
    agent_menu(update, context)

def agent_menu(update, context):
    """نمایش منوی اصلی نمایندگی."""
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
    """نمایش لیست استان‌ها برای انتخاب."""
    keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in PROVINCES_CITIES.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً استان خود را انتخاب کنید:"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def show_cities(update, context, province):
    """نمایش شهرهای استان انتخاب‌شده."""
    cities = PROVINCES_CITIES[province]  # لیست شهرها بر اساس استان انتخاب شده
    keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"لطفاً یکی از شهرهای استان {province} را انتخاب کنید:"

    # ارسال پیام به همراه دکمه‌های شیشه‌ای شهرها
    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def handle_province_selection(update, context):
    """مدیریت انتخاب استان توسط نماینده."""
    province = update.callback_query.data.split('_')[1]  # استخراج نام استان از داده callback
    context.user_data['current_province'] = province  # ذخیره استان انتخاب شده در user_data
    show_cities(update, context, province)  # نمایش لیست شهرهای استان انتخاب شده


def find_next_product_id(data):
    """یافتن اولین شماره خالی برای محصول."""
    used_product_ids = set(map(int, data.get('products', {}).keys()))
    product_id = 1
    while product_id in used_product_ids:
        product_id += 1
    return product_id


def handle_city_selection(update, context):
    """مدیریت انتخاب شهر توسط نماینده و هدایت به ذخیره محصول."""
    city = update.callback_query.data.split('_')[1]
    context.user_data['current_city'] = city  # ذخیره شهر انتخاب شده

    # هدایت به تابع ذخیره محصول پس از انتخاب شهر
    save_new_product(update, context)

    # پاسخ به نماینده
    update.callback_query.answer()






def add_product(update, context):
    """درخواست اطلاعات محصول جدید از نماینده."""
    if update.callback_query:
        update.callback_query.message.reply_text("نام محصول را وارد کنید.")
        update.callback_query.answer()
        context.user_data['adding_product'] = True

def handle_message(update, context):
    """مدیریت پیام‌های کاربر برای افزودن محصول."""
    if context.user_data.get('adding_product'):
        process_product_details(update, context)

def process_product_details(update, context):
    """فرآیند دریافت و ذخیره جزئیات محصول جدید."""
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
            show_provinces(update, context)  # درخواست انتخاب استان پس از وارد کردن موجودی
        else:
            update.message.reply_text("لطفاً یک عدد معتبر برای موجودی وارد کنید.")
    elif 'current_city' in context.user_data:
        save_new_product(update, context)

def save_new_product(update, context):
    """ذخیره محصول جدید در پایگاه داده."""
    # بارگیری داده‌ها از فایل JSON
    data = load_data()

    # گرفتن اطلاعات از context.user_data
    product_name = context.user_data.get('product_name')
    product_description = context.user_data.get('product_description')
    product_price = context.user_data.get('product_price')
    product_stock = context.user_data.get('product_stock')  # موجودی محصول
    city = context.user_data.get('current_city')
    province = context.user_data.get('current_province')
    agent_id = str(update.effective_user.id)

    # یافتن اولین شماره خالی برای محصول
    product_id = find_next_product_id(data)

    # ایجاد ورودی جدید برای محصول در بخش products
    if 'products' not in data:
        data['products'] = {}
    data['products'][product_id] = {
        'name': product_name,
        'description': product_description,
        'price': product_price,
        'stock': product_stock,
        'sold': 0,  # تعداد فروخته شده (ابتدایی 0)
        'province': province,
        'city': city,
        'agent_id': agent_id
    }

    # اطمینان از وجود بخش agents و افزودن شماره محصول به آن
    if 'agents' not in data:
        data['agents'] = {}
    if agent_id not in data['agents']:
        data['agents'][agent_id] = {'products': []}

    # افزودن شماره محصول به لیست محصولات نماینده در بخش agents
    data['agents'][agent_id]['products'].append(product_id)

    # ذخیره داده‌ها در فایل JSON
    save_data(data)

    # ارسال پیام به نماینده برای تأیید (اطلاعات محصول از data['products'][product_id])
    product_details = (
        f"محصول شما با موفقیت اضافه شد:\n"
        f"نام: {data['products'][product_id]['name']}\n"
        f"توضیحات: {data['products'][product_id]['description']}\n"
        f"قیمت: {data['products'][product_id]['price']} تومان\n"
        f"موجودی: {data['products'][product_id]['stock']} عدد\n"
        f"تعداد فروخته شده: {data['products'][product_id]['sold']}\n"
        f"شهر: {data['products'][product_id]['city']}\n"
    )
    update.callback_query.message.reply_text(product_details)

    # پاک‌سازی context.user_data پس از افزودن محصول
    context.user_data.clear()



handle_new_product = handle_message







def list_my_products(update, context):
    """نمایش لیست محصولات نماینده."""
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