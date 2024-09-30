import json
from config import DATABASE

def load_data():
    with open(DATABASE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATABASE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user(user_id):
    data = load_data()
    return data["users"].get(str(user_id))

def update_user(user_id, user_data):
    data = load_data()
    data["users"][str(user_id)] = user_data
    save_data(data)

def add_product_to_cart(user_id, product_id, quantity):
    data = load_data()
    user = data["users"].get(str(user_id))
    product = get_product_by_id(product_id)
    if product:
        if product_id in user["cart"]:
            user["cart"][product_id]["quantity"] += quantity
        else:
            user["cart"][product_id] = {"name": product["name"], "price": product["price"], "quantity": quantity}
    update_user(user_id, user)

def get_product_by_id(product_id):
    data = load_data()
    for city in data["agents"]:
        products = data["agents"][city]["products"]
        if product_id in products:
            return products[product_id]
    return None

def confirm_payment(user_id, amount):
    data = load_data()
    user = data["users"][str(user_id)]
    user["balance"] += amount
    update_user(user_id, user)

def create_order(user_id):
    data = load_data()
    user = data["users"].get(str(user_id))
    new_order_id = len(user["orders"]) + 1
    order = {
        "order_id": new_order_id,
        "products": user["cart"],
        "status": "pending"
    }
    user["orders"].append(order)
    user["cart"] = {}
    update_user(user_id, user)
    return new_order_id
