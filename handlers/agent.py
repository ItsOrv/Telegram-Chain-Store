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
    agent_menu(update, context)

def show_provinces(update, context):
    keyboard = [[InlineKeyboardButton(province, callback_data=f"province_{province}")] for province in PROVINCES_CITIES.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "لطفاً استان خود را انتخاب کنید:"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def show_cities(update, context, province):
    cities = PROVINCES_CITIES[province]
    keyboard = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in cities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"شهرهای استان {province} را انتخاب کنید:"

    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()

def handle_province_selection(update, context):
    province = update.callback_query.data.split('_')[1]
    show_cities(update, context, province)

def handle_city_selection(update, context):
    city = update.callback_query.data.split('_')[1]
    context.user_data['current_city'] = city
    update.callback_query.answer()

def agent_menu(update, context):
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

def list_my_products(update, context):
    user_id = update.effective_user.id
    data = load_data()
    products = data["agents"].get(context.user_data.get("current_city", ""), {}).get("products", {})

    message = "محصولات شما:\n"
    for product_id, product in products.items():
        message += f"{product['name']} - قیمت: {product['price']} - موجودی: {product['stock']}\n"

    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)
        update.callback_query.answer()

def add_product(update, context):
    if update.callback_query:
        update.callback_query.message.reply_text("نام محصول را وارد کنید.")
        update.callback_query.answer()
        context.user_data['adding_product'] = True

def handle_message(update, context):
    user_id = update.effective_user.id

    if context.user_data.get('adding_product'):
        if 'new_product_name' not in context.user_data:
            context.user_data['new_product_name'] = update.message.text
            update.message.reply_text("توضیحات محصول را وارد کنید.")
        elif 'new_product_description' not in context.user_data:
            context.user_data['new_product_description'] = update.message.text
            update.message.reply_text("قیمت محصول را وارد کنید.")
        elif 'new_product_price' not in context.user_data:
            price_text = update.message.text
            if price_text.isdigit():
                context.user_data['new_product_price'] = int(price_text)
                show_provinces(update, context)
            else:
                update.message.reply_text("لطفاً یک قیمت معتبر وارد کنید.")
        elif 'current_city' in context.user_data:
            save_new_product(update, context, user_id)

def save_new_product(update, context, user_id):
    data = load_data()
    city = context.user_data['current_city']

    new_product = {
        "name": context.user_data['new_product_name'],
        "description": context.user_data['new_product_description'],
        "price": context.user_data['new_product_price'],
        "stock": 0,
        "location": {
            "province": "province_name",  # باید این را بر اساس انتخاب کاربر تعیین کنید
            "city": city
        }
    }

    if city not in data["agents"]:
        data["agents"][city] = {"agent_id": user_id, "products": {}}

    data["agents"][city]["products"][context.user_data['new_product_name']] = new_product
    save_data(data)

    product_details = (
        f"محصول شما با مشخصات زیر اضافه شد:\n"
        f"نام: {new_product['name']}\n"
        f"توضیحات: {new_product['description']}\n"
        f"قیمت: {new_product['price']}\n"
    )
    update.message.reply_text(product_details)

    # Clean up user data
    context.user_data.clear()
