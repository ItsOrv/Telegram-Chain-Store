from utils.helpers import load_data, update_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    user_id = update.message.from_user.id
    data = load_data()
    user = data["users"].get(str(user_id))
    
    if not user:
        new_user = {
            "role": "customer",
            "balance": 0,
            "city": "",
            "cart": {},
            "orders": []
        }
        data["users"][str(user_id)] = new_user
        update_user(user_id, new_user)
    
    if user and user["role"] == "admin":
        from handlers.admin import admin_menu
        admin_menu(update, context)
    elif user and user["role"] == "agent":
        from handlers.agent import agent_menu
        agent_menu(update, context)
    else:
        from handlers.customer import customer_menu
        customer_menu(update, context)
