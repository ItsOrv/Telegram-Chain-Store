from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from handlers import admin, agent, customer, common

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", common.start))  # شروع

    # Admin handlers
    dp.add_handler(CallbackQueryHandler(admin.add_category, pattern='add_category'))  # اضافه کردن دسته‌بندی
    dp.add_handler(CallbackQueryHandler(admin.manage_categories, pattern='manage_categories'))  # مدیریت دسته‌بندی‌ها
    dp.add_handler(CallbackQueryHandler(admin.delete_category, pattern='delete_category'))  # حذف دسته‌بندی
    dp.add_handler(CallbackQueryHandler(admin.list_agents, pattern='list_agents'))  # لیست نمایندگان
    dp.add_handler(CallbackQueryHandler(admin.add_agent_start, pattern='add_agent'))
    dp.add_handler(CallbackQueryHandler(admin.admin_manage_products, pattern='admin_manage_products'))
    dp.add_handler(CallbackQueryHandler(admin.edit_category, pattern='edit_category'))

    dp.add_handler(CallbackQueryHandler(admin.admin_delete_product, pattern='admin_delete_product'))
    dp.add_handler(CallbackQueryHandler(admin.admin_edit_product, pattern='admin_edit_product'))

    dp.add_handler(CallbackQueryHandler(admin.admin_report, pattern='reports'))  # نمایش سفارشات
    # edit_category


    # Agent handlers
    dp.add_handler(CallbackQueryHandler(agent.add_product, pattern='add_product'))  # اضافه کردن محصول
    dp.add_handler(CallbackQueryHandler(agent.list_my_products, pattern='list_my_products'))  # نمایش محصولات
    dp.add_handler(CallbackQueryHandler(agent.handle_province_selection, pattern=r'province_'))  # انتخاب استان
    dp.add_handler(CallbackQueryHandler(agent.handle_city_selection, pattern=r'city_'))  # انتخاب شهر
    dp.add_handler(CallbackQueryHandler(agent.handle_category_selection, pattern=r'category_'))


    # Customer handlers
    dp.add_handler(CallbackQueryHandler(customer.buy_product, pattern='buy_product'))  # خرید محصول
    dp.add_handler(CallbackQueryHandler(customer.show_cart, pattern='show_cart'))  # نمایش سبد خرید
    dp.add_handler(CallbackQueryHandler(customer.previous_orders, pattern='previous_orders'))  # نمایش سفارشات قبلی
    dp.add_handler(CallbackQueryHandler(customer.charge_account, pattern='charge_account'))  # شارژ حساب

    # Text message handlers برای متن‌های وارد شده توسط کاربر
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, agent.handle_new_product))  # مدیریت متن مربوط به اضافه کردن محصول
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, admin.handle_new_category))  # مدیریت متن مربوط به اضافه کردن دسته‌بندی
    # handle_edit_message
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.regex(r'^\d+$'), customer.handle_charge_account))  # مدیریت شارژ حساب (فقط اعداد مثبت)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, common.handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



# دکمه لیست نماینده ها 
# بررسی دوباره ادیت محصولات ادمین
# به محصولات متغیر دسته بندی هم اضافه شود