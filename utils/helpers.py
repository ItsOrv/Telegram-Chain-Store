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
def create_order(user_id):
    data = load_data()
    user = data["users"].get(str(user_id))

    if not user or not user.get("cart"):
        return None  # اگر کاربر یا سبد خرید وجود نداشته باشد
    
    new_order_id = len(user["orders"]) + 1
    order = {
        "order_id": new_order_id,
        "products": user["cart"],
        "status": "pending"
    }
    user["orders"].append(order)
    user["cart"] = {}  # خالی کردن سبد خرید پس از ایجاد سفارش
    update_user(user_id, user)
    return new_order_id
