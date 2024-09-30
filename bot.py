from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from handlers import admin, agent, customer, common
from handlers.admin import handle_new_category  # اضافه کردن ایمپورت تابع
from handlers.agent import handle_new_product  # اضافه کردن هندلر متن محصول

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", common.start))

    # Admin handlers
    dp.add_handler(CallbackQueryHandler(admin.list_agents, pattern='list_agents'))
    dp.add_handler(CallbackQueryHandler(admin.add_category_start, pattern='add_category'))  # شروع اضافه کردن دسته‌بندی
    dp.add_handler(CallbackQueryHandler(admin.manage_categories, pattern='manage_categories'))  # مدیریت دسته‌بندی‌ها

    # Agent handlers
    dp.add_handler(CallbackQueryHandler(agent.add_product, pattern='add_product'))  # اضافه کردن محصول
    dp.add_handler(CallbackQueryHandler(agent.list_my_products, pattern='list_my_products'))  # نمایش محصولات
    dp.add_handler(CallbackQueryHandler(agent.handle_province_selection, pattern=r'province_'))  # انتخاب استان
    dp.add_handler(CallbackQueryHandler(agent.handle_city_selection, pattern=r'city_'))  # انتخاب شهر

    # Customer handlers
    dp.add_handler(CallbackQueryHandler(customer.buy_product, pattern='buy_product'))  # خرید محصول
    dp.add_handler(CallbackQueryHandler(customer.show_cart, pattern='show_cart'))  # نمایش سبد خرید
    dp.add_handler(CallbackQueryHandler(customer.previous_orders, pattern='previous_orders'))  # نمایش سفارشات قبلی
    dp.add_handler(CallbackQueryHandler(customer.charge_account, pattern='charge_account'))  # شارژ حساب

    # Text message handlers برای متن‌های وارد شده توسط کاربر
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r'^\d+$'), handle_new_product))  # مدیریت متن مربوط به اضافه کردن محصول
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r'^[a-zA-Z]+$'), handle_new_category))  # مدیریت متن مربوط به اضافه کردن دسته‌بندی

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
