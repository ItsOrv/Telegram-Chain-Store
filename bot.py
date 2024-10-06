from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from handlers import admin, agent, customer, common

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", common.start))  # شروع

    # Admin handlers
    dp.add_handler(CallbackQueryHandler(admin.admin_menu, pattern='admin_menu'))
    dp.add_handler(CallbackQueryHandler(admin.add_category, pattern='add_category'))  # اضافه کردن دسته‌بندی
    dp.add_handler(CallbackQueryHandler(admin.manage_categories, pattern='manage_categories'))  # مدیریت دسته‌بندی‌ها
    dp.add_handler(CallbackQueryHandler(admin.delete_category, pattern='delete_category'))  # حذف دسته‌بندی
    dp.add_handler(CallbackQueryHandler(admin.list_agents, pattern='list_agents'))  # لیست نمایندگان
    dp.add_handler(CallbackQueryHandler(admin.add_agent_start, pattern='add_agent'))
    dp.add_handler(CallbackQueryHandler(admin.admin_manage_single_product, pattern='admin_manage_single_product'))
    dp.add_handler(CallbackQueryHandler(admin.edit_category, pattern='edit_category'))
    dp.add_handler(CallbackQueryHandler(admin.add_agent, pattern='add_agent'))


    dp.add_handler(CallbackQueryHandler(admin.manage_agent, pattern='manage_agent_'))
    dp.add_handler(CallbackQueryHandler(admin.get_report, pattern='get_report_'))
    dp.add_handler(CallbackQueryHandler(admin.delete_agent, pattern='delete_agent_'))



    dp.add_handler(CallbackQueryHandler(admin.admin_delete_product, pattern='admin_delete_product'))
    dp.add_handler(CallbackQueryHandler(admin.admin_edit_product, pattern='admin_edit_product'))

    dp.add_handler(CallbackQueryHandler(admin.admin_report, pattern='reports'))  # نمایش سفارشات
    # edit_category


    # Agent handlers
    dp.add_handler(CallbackQueryHandler(agent.add_product, pattern='add_product'))  # اضافه کردن محصول
    dp.add_handler(CallbackQueryHandler(agent.list_my_products, pattern='list_my_products'))  # نمایش محصولات
    #dp.add_handler(CallbackQueryHandler(agent.handle_province_selection, pattern=r'province_'))  # انتخاب استان
    #dp.add_handler(CallbackQueryHandler(agent.handle_city_selection, pattern=r'city_'))  # انتخاب شهر
    dp.add_handler(CallbackQueryHandler(agent.handle_category_selection, pattern=r'category_'))


    # Customer handlers

# خرید محصول
    dp.add_handler(CallbackQueryHandler(customer.buy_product, pattern='buy_product'))  # خرید محصول

# انتخاب استان
    dp.add_handler(CallbackQueryHandler(customer.handle_province_selection, pattern=r'province_'))  # انتخاب استان

# انتخاب شهر
    dp.add_handler(CallbackQueryHandler(customer.handle_city_selection, pattern=r'city_'))  # انتخاب شهر

# انتخاب محصول
    dp.add_handler(CallbackQueryHandler(customer.handle_product_selection, pattern=r'product_'))  # انتخاب محصول

# نمایش سبد خرید
    dp.add_handler(CallbackQueryHandler(customer.show_cart, pattern='show_cart'))  # نمایش سبد خرید

# نمایش سفارشات قبلی
    dp.add_handler(CallbackQueryHandler(customer.previous_orders, pattern='previous_orders'))  # نمایش سفارشات قبلی

# شارژ حساب
    dp.add_handler(CallbackQueryHandler(customer.charge_account, pattern='charge_account'))  # شارژ حساب
    dp.add_handler(CallbackQueryHandler(customer.handle_add_product, pattern=r'add_\d+'))  # برای افزایش تعداد
    dp.add_handler(CallbackQueryHandler(customer.handle_remove_product, pattern=r'remove_\d+'))  # برای کاهش تعداد
        # Callback query handlers

    dp.add_handler(CallbackQueryHandler(customer.handle_add_product, pattern=r'add_'))
    dp.add_handler(CallbackQueryHandler(customer.handle_remove_product, pattern=r'remove_'))
    #dp.add_handler(CallbackQueryHandler(customer.confirm_order, pattern='confirm_order'))

    dp.add_handler(CallbackQueryHandler(customer.previous_orders, pattern='previous_orders'))

    dp.add_handler(CallbackQueryHandler(customer.contact_admin, pattern='contact_admin'))

    dp.add_handler(CallbackQueryHandler(customer.remove_from_cart, pattern='remove_from_cart'))

    dp.add_handler(CallbackQueryHandler(customer.card_to_card_payment, pattern='card_to_card_payment'))
    dp.add_handler(CallbackQueryHandler(customer.crypto_payment, pattern='crypto_payment'))
    
    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='handle_back'))

    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='back_to_main_menu'))
    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='back_to_buy_product'))
    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='back_to_province_selection'))
    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='back_to_city_selection'))
    dp.add_handler(CallbackQueryHandler(customer.handle_back, pattern='back_to_product_list'))
    #dp.add_handler(CallbackQueryHandler(customer.add_product_to_cart, pattern=r'add_to_cart_\d+'))

    dp.add_handler(CallbackQueryHandler(customer.handle_cancel_product_message, pattern='cancel_product_message'))



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
