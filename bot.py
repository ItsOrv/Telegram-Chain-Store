from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from handlers import admin, agent, customer, common

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", common.start))

    # Admin handlers
    dp.add_handler(CallbackQueryHandler(admin.admin_menu, pattern='admin_menu')) 
    dp.add_handler(CallbackQueryHandler(admin.admin_manage_categories, pattern='admin_manage_categories'))
    dp.add_handler(CallbackQueryHandler(admin.admin_add_category, pattern='admin_add_category'))
    dp.add_handler(CallbackQueryHandler(admin.admin_delete_category, pattern='admin_delete_category'))
    dp.add_handler(CallbackQueryHandler(admin.admin_list_agents, pattern='admin_list_agents'))
    dp.add_handler(CallbackQueryHandler(admin.admin_add_agent_start, pattern='admin_add_agent'))
    dp.add_handler(CallbackQueryHandler(admin.admin_manage_single_product, pattern='admin_manage_single_product'))
    dp.add_handler(CallbackQueryHandler(admin.admin_edit_category, pattern='admin_edit_category'))
    dp.add_handler(CallbackQueryHandler(admin.admin_add_agent, pattern='admin_add_agent'))
    dp.add_handler(CallbackQueryHandler(admin.admin_manage_agent, pattern='admin_manage_agent'))
    dp.add_handler(CallbackQueryHandler(admin.admin_get_report, pattern='admin_get_report_'))
    dp.add_handler(CallbackQueryHandler(admin.admin_delete_agent, pattern='admin_delete_agent_'))
    dp.add_handler(CallbackQueryHandler(admin.admin_delete_product, pattern='admin_delete_product_'))
    dp.add_handler(CallbackQueryHandler(admin.admin_edit_product, pattern='admin_edit_product_'))
    dp.add_handler(CallbackQueryHandler(admin.admin_report, pattern='admin_report'))


    # Agent handlers
    dp.add_handler(CallbackQueryHandler(agent.agent_menu, pattern='agent_menu'))
    dp.add_handler(CallbackQueryHandler(agent.agent_add_product, pattern='agent_add_product'))
    dp.add_handler(CallbackQueryHandler(agent.agent_show_provinces, pattern='agent_show_provinces'))
    dp.add_handler(CallbackQueryHandler(agent.agent_handle_province_selection, pattern='agent_province_'))
    dp.add_handler(CallbackQueryHandler(agent.agent_show_cities, pattern='agent_show_cities'))
    dp.add_handler(CallbackQueryHandler(agent.agent_handle_city_selection, pattern='agent_city_'))
    dp.add_handler(CallbackQueryHandler(agent.agent_handle_category_selection, pattern='agent_category_'))
    dp.add_handler(CallbackQueryHandler(agent.agent_edit_product, pattern='agent_edit_product'))
    dp.add_handler(CallbackQueryHandler(agent.agent_delete_product, pattern='agent_delete_product'))
    dp.add_handler(CallbackQueryHandler(agent.agent_save_new_product, pattern='agent_save_new_product'))
    dp.add_handler(CallbackQueryHandler(agent.agent_find_next_product_id, pattern='agent_find_next_product_id'))
    dp.add_handler(CallbackQueryHandler(agent.agent_show_categories, pattern='agent_show_categories'))
    dp.add_handler(CallbackQueryHandler(agent.agent_list_my_products, pattern='agent_list_my_products')) 

    # Customer handlers
    dp.add_handler(CallbackQueryHandler(customer.customer_menu, pattern='customer_menu'))
    dp.add_handler(CallbackQueryHandler(customer.customer_buy_product, pattern='customer_buy_product'))  # خرید محصول
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_province_selection, pattern='customer_province_'))  # انتخاب استان
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_city_selection, pattern='customer_city_'))  # انتخاب شهر
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_product_selection, pattern='customer_product_'))  # انتخاب محصول
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_cancel_product_message, pattern='customer_cancel_product_message'))
    dp.add_handler(CallbackQueryHandler(customer.customer_add_product_to_cart, pattern=r'add_to_cart_\d+'))
    dp.add_handler(CallbackQueryHandler(customer.customer_show_cart, pattern='customer_show_cart'))  # نمایش سبد خرید
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_add_product, pattern=r'customer_add_'))  # برای افزایش تعداد
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_remove_product, pattern=r'customer_remove_'))
    dp.add_handler(CallbackQueryHandler(customer.customer_confirm_order, pattern='customer_confirm_order'))
    dp.add_handler(CallbackQueryHandler(customer.customer_card_to_card_payment, pattern='customer_card_to_card_payment'))
    
    #notpass
    dp.add_handler(CallbackQueryHandler(customer.handle_payment_confirmation, pattern='handle_payment_confirmation'))
    dp.add_handler(CallbackQueryHandler(customer.handle_admin_decision, pattern='handle_admin_decision'))
    dp.add_handler(CallbackQueryHandler(customer.confirm_payment, pattern='confirm_payment'))
    dp.add_handler(CallbackQueryHandler(customer.cancel_order, pattern='cancel_order'))

    
    '''
    dp.add_handler(CallbackQueryHandler(customer.customer_previous_orders, pattern='customer_previous_orders'))  # نمایش سفارشات قبلی
    dp.add_handler(CallbackQueryHandler(customer.customer_charge_account, pattern='customer_charge_account'))  # شارژ حساب
    dp.add_handler(CallbackQueryHandler(customer.customer_contact_admin, pattern='customer_contact_admin'))
    dp.add_handler(CallbackQueryHandler(customer.customer_remove_from_cart, pattern='customer_remove_from_cart'))
    dp.add_handler(CallbackQueryHandler(customer.customer_crypto_payment, pattern='customer_crypto_payment'))
    dp.add_handler(CallbackQueryHandler(customer.customer_pay_with_balance, pattern='customer_pay_with_balance'))

    dp.add_handler(CallbackQueryHandler(customer.customer_handle_back, pattern='customer_back_to_buy_product'))
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_back, pattern='customer_back_to_province_selection'))
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_back, pattern='customer_back_to_city_selection'))
    dp.add_handler(CallbackQueryHandler(customer.customer_handle_back, pattern='customer_back_to_product_list'))
    '''


    # Text message handlers
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, common.handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
