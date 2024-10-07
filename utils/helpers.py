import json
from config import DATABASE

# بارگذاری اطلاعات از فایل JSON
def load_data():
    with open(DATABASE, 'r', encoding='utf-8') as f:
        return json.load(f)

# ذخیره اطلاعات در فایل JSON
def save_data(data):
    with open(DATABASE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# دریافت اطلاعات کاربر از طریق شناسه کاربر
def get_user(user_id):
    data = load_data()
    return data["users"].get(str(user_id))

# به‌روزرسانی اطلاعات کاربر در فایل JSON
def update_user(user_id, user_data):
    data = load_data()
    data["users"][str(user_id)] = user_data
    save_data(data)

# افزودن محصول به سبد خرید کاربر
def add_product_to_cart(user_id, product_id, quantity=1):
    data = load_data()
    user = data["users"].get(str(user_id))

    if not user:
        return False  # اگر کاربر یافت نشد

    product = get_product_by_id(product_id)
    
    if not product:
        return False  # اگر محصول یافت نشد
    
    # اضافه کردن یا به‌روزرسانی محصول در سبد خرید
    if product_id in user["cart"]:
        user["cart"][product_id]["quantity"] += quantity
    else:
        user["cart"][product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        }

    update_user(user_id, user)
    return True

# دریافت اطلاعات محصول از طریق شناسه محصول
def get_product_by_id(product_id):
    data = load_data()
    for agent_info in data["agents"].values():
        products = agent_info["products"]
        if product_id in products:
            return products[product_id]
    return None

# تأیید پرداخت و شارژ حساب کاربر
def confirm_payment(user_id, amount):
    data = load_data()
    user = data["users"].get(str(user_id))
    
    if not user:
        return False  # اگر کاربر یافت نشد

    user["balance"] += amount
    update_user(user_id, user)
    return True

# ایجاد سفارش جدید برای کاربر
def create_order(user_id, cart):
    data = load_data()
    user = data["users"].get(str(user_id))

    if not user or not cart:
        return None  # اگر کاربر یا سبد خرید وجود نداشته باشد
    
    new_order_id = len(user["orders"]) + 1
    order = {
        "order_id": new_order_id,
        "products": cart,
        "status": "pending"
    }
    user["orders"].append(order)
    user["cart"] = {}  # خالی کردن سبد خرید پس از ایجاد سفارش
    update_user(user_id, user)
    return new_order_id










# for next update
'''
def edit_name(update, context):
    """Ask agent to provide a new name for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'name'

    query.edit_message_text("لطفاً نام جدید محصول را وارد کنید.")
    
def save_new_name(update, context):
    """Save the new name of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_name = update.message.text
    
    if product_id:
        update_product_in_database(product_id, 'name', new_name)  # به‌روزرسانی نام در دیتابیس
        update.message.reply_text(f"نام محصول به {new_name} تغییر یافت.")
    else:
        update.message.reply_text("خطایی رخ داده است.")


def edit_description(update, context):
    """Ask agent to provide a new description for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]

    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'description'

    query.edit_message_text("لطفاً توضیحات جدید محصول را وارد کنید.")
    
def save_new_description(update, context):
    """Save the new description of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_description = update.message.text

    if product_id:
        update_product_in_database(product_id, 'description', new_description)  # به‌روزرسانی توضیحات در دیتابیس
        update.message.reply_text(f"توضیحات محصول تغییر یافت.")
    else:
        update.message.reply_text("خطایی رخ داده است.")


def edit_price(update, context):
    """Ask agent to provide a new price for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]

    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'price'

    query.edit_message_text("لطفاً قیمت جدید محصول را وارد کنید.")
    
def save_new_price(update, context):
    """Save the new price of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_price = update.message.text

    if new_price.isdigit():  # بررسی اینکه قیمت باید عدد معتبر باشد
        update_product_in_database(product_id, 'price', int(new_price))  # به‌روزرسانی قیمت در دیتابیس
        update.message.reply_text(f"قیمت محصول تغییر یافت.")
    else:
        update.message.reply_text("لطفاً یک قیمت معتبر وارد کنید.")


def edit_stock(update, context):
    """Ask agent to provide a new stock for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]

    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'stock'

    query.edit_message_text("لطفاً موجودی جدید محصول را وارد کنید.")
    
def save_new_stock(update, context):
    """Save the new stock of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_stock = update.message.text

    if new_stock.isdigit():  # بررسی اینکه موجودی باید عدد معتبر باشد
        update_product_in_database(product_id, 'stock', int(new_stock))  # به‌روزرسانی موجودی در دیتابیس
        update.message.reply_text(f"موجودی محصول تغییر یافت.")
    else:
        update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")


def edit_location(update, context):
    """Ask agent to select a new province and city for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]

    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'location'

    # نمایش لیست استان‌ها
    agent_show_provinces(update, context)  # همان فانکشن قبلی برای نمایش لیست استان‌ها
    
def save_new_location(update, context):
    """Save the new location (province and city) of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_province = context.user_data.get('new_province')
    new_city = update.message.text  # فرض می‌کنیم کاربر پس از انتخاب استان، شهر جدید را وارد می‌کند

    if product_id and new_province and new_city:
        update_product_in_database(product_id, 'province', new_province)
        update_product_in_database(product_id, 'city', new_city)  # به‌روزرسانی استان و شهر در دیتابیس
        update.message.reply_text(f"مکان محصول تغییر یافت.")
    else:
        update.message.reply_text("لطفاً یک مکان معتبر انتخاب کنید.")


def edit_category(update, context):
    """Ask agent to select a new category for the product."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]

    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'category'

    # نمایش لیست دسته‌بندی‌ها
    agent_show_categories(update, context)  # نمایش لیست دسته‌بندی‌ها
    

def save_new_category(update, context):
    """Save the new category of the product."""
    product_id = context.user_data.get('editing_product_id')
    new_category = update.message.text  # فرض می‌کنیم کاربر دسته‌بندی جدید را انتخاب کرده است

    if product_id and new_category:
        update_product_in_database(product_id, 'category', new_category)  # به‌روزرسانی دسته‌بندی در دیتابیس
        update.message.reply_text(f"دسته‌بندی محصول تغییر یافت.")
    else:
        update.message.reply_text("لطفاً یک دسته‌بندی معتبر انتخاب کنید.")


def get_agent_products(agent_id):
    """Retrieve the list of products associated with an agent."""
    with open('data/products.json', 'r') as file:
        products = json.load(file)

    # فیلتر محصولات بر اساس شناسه نماینده
    agent_products = [product for product in products if product['agent_id'] == agent_id]
    return agent_products


def delete_product_from_database(product_id):
    """Delete a product from the JSON database."""
    with open('data/products.json', 'r') as file:
        products = json.load(file)

    # فیلتر کردن محصولات به جز محصولی که باید حذف شود
    updated_products = [product for product in products if product['product_id'] != product_id]

    with open('data/products.json', 'w') as file:
        json.dump(updated_products, file, ensure_ascii=False, indent=4)

    print(f"Product {product_id} deleted from the database.")


def update_product_in_database(product_id, field, new_value):
    """Update a specific field of a product in the JSON database."""
    with open('data/products.json', 'r') as file:
        products = json.load(file)

    for product in products:
        if product['product_id'] == product_id:
            product[field] = new_value
            break

    with open('data/products.json', 'w') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

    print(f"Product {product_id} updated. {field} set to {new_value}.")
'''