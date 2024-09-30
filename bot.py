from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from handlers import admin, agent, customer, common
from handlers.admin import handle_new_category  # اضافه کردن ایمپورت تابع

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", common.start))

    # Admin handlers
    dp.add_handler(CallbackQueryHandler(admin.list_agents, pattern='list_agents'))
    dp.add_handler(CallbackQueryHandler(admin.add_category, pattern='add_category'))

    # Agent handlers
    dp.add_handler(CallbackQueryHandler(agent.add_product, pattern='add_product'))
    dp.add_handler(CallbackQueryHandler(agent.list_my_products, pattern='list_my_products'))
    dp.add_handler(CallbackQueryHandler(agent.handle_province_selection, pattern=r'province_'))
    dp.add_handler(CallbackQueryHandler(agent.handle_city_selection, pattern=r'city_'))

    # Customer handlers
    dp.add_handler(CallbackQueryHandler(customer.buy_product, pattern='buy_product'))
    dp.add_handler(CallbackQueryHandler(customer.show_cart, pattern='show_cart'))
    dp.add_handler(CallbackQueryHandler(customer.previous_orders, pattern='previous_orders'))
    dp.add_handler(CallbackQueryHandler(customer.charge_account, pattern='charge_account'))

    # Text message handlers (اینجا تابع handle_new_category را اضافه می‌کنیم)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_new_category))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
