from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_data, save_data

#pass
def admin_menu(update, context):
    """
    Displays the main admin menu with options for managing categories, products, agents, 
    and generating reports.
    """
    keyboard = [
        [InlineKeyboardButton("مدیریت دسته‌بندی‌ها", callback_data='admin_manage_categories')],
        [InlineKeyboardButton("مدیریت محصولات و نماینده‌ها", callback_data='admin_list_agents')],
        [InlineKeyboardButton("افزودن نماینده", callback_data='admin_add_agent_start')],
        [InlineKeyboardButton("گزارش‌گیری", callback_data='admin_report')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "به پنل ادمین خوش آمدید"

    if update.callback_query:
        update.callback_query.message.delete()
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def admin_manage_categories(update, context):
    """
    Allows the admin to manage categories by displaying relevant buttons for each category,
    including options to add, edit, or delete categories.
    """
    data = load_data()
    categories = data.get("categories", [])

    keyboard = [[InlineKeyboardButton("افزودن دسته‌بندی", callback_data='admin_add_category')]]
    for category in categories:
        keyboard.append([InlineKeyboardButton(f"{category}", callback_data=f'view_category_{category}')])
        keyboard.append([
            InlineKeyboardButton("ویرایش", callback_data=f'admin_edit_category_{category}'),
            InlineKeyboardButton("حذف", callback_data=f'admin_delete_category_{category}')
        ])

    # Add a return button to the main admin menu
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data='admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "مدیریت دسته‌بندی‌ها"

    if update.callback_query:
        update.callback_query.message.delete()
        update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

#pass
def admin_add_category(update, context):
    """
    Requests the name of a new category from the admin to add it to the system.
    """
    if update.callback_query:
        # Remove the previous inline keyboard if present
        # update.callback_query.edit_message_reply_markup(reply_markup=None)

        update.callback_query.message.reply_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data['adding_category'] = True
        update.callback_query.answer()

#pass
def admin_handle_new_category(update, context):
    """
    Handles the addition of a new category. Ensures the category name doesn't already exist.
    """
    if context.user_data.get('adding_category'):
        new_category = update.message.text.strip()
        data = load_data()

        if 'categories' not in data:
            data['categories'] = []

        if new_category not in data['categories']:
            data['categories'].append(new_category)
            save_data(data)

            confirmation_message = update.message.reply_text(f"دسته‌بندی '{new_category}' با موفقیت اضافه شد.")

            # Optionally remove confirmation and request messages after a short time
            # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
            # update.message.delete()

            # Update the category management menu
            admin_manage_categories(update, context)
        else:
            update.message.reply_text(f"دسته‌بندی '{new_category}' قبلاً وجود دارد.")
            admin_manage_categories(update, context)

        context.user_data['adding_category'] = False
    else:
        update.message.reply_text("ابتدا از منوی مدیریت دسته‌بندی‌ها اقدام کنید.")
        admin_manage_categories(update, context)

#pass
def admin_edit_category(update, context):
    """
    Requests a new name for the selected category from the admin for renaming purposes.
    """
    query = update.callback_query
    category = query.data.split('_')[-1]

    # Remove the previous inline keyboard if present
    # query.edit_message_reply_markup(reply_markup=None)

    # Send a message requesting the new name for the category
    query.message.reply_text(f"نام جدید دسته‌بندی '{category}' را وارد کنید:")
    context.user_data['editing_category'] = category
    query.answer()

#pass
def admin_handle_edit_message(update, context):
    """Handles editing of a category name."""
    if 'editing_category' in context.user_data:
        old_category = context.user_data['editing_category']  # Retrieve the old category name
        new_category = update.message.text.strip()  # Get the new category name entered by the user
        data = load_data()  # Load the current data from the database or file

        # Check if the new category already exists
        if new_category in data.get("categories", []):
            update.message.reply_text("This category already exists.")  # Notify if the category already exists
        else:
            # Update the categories by removing the old and adding the new category
            data['categories'].remove(old_category)
            data['categories'].append(new_category)
            save_data(data)  # Save the updated data

            confirmation_message = update.message.reply_text(f"Category '{old_category}' has been changed to '{new_category}'.")

            # Optionally delete confirmation message and the request message
            # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
            # update.message.delete()

            # Refresh the category management menu
            admin_manage_categories(update, context)

        # Clear the user data after the process is complete
        context.user_data.clear()

#pass
def admin_delete_category(update, context):
    """Handles the deletion of a category."""
    query = update.callback_query
    category = query.data.split('_')[-1]  # Extract the category to delete from callback data
    data = load_data()  # Load current data

    # Check if the category exists in the data
    if category in data.get("categories", []):
        data['categories'].remove(category)  # Remove the category from the list
        save_data(data)  # Save the updated data

        confirmation_message = query.message.reply_text(f"Category '{category}' has been deleted.")

        # Optionally delete confirmation message, previous messages, and inline keyboard
        # (This part might require additional handling)

        # Refresh the category management menu
        admin_manage_categories(update, context)
        # context.job_queue.run_once(lambda _: confirmation_message.delete(), 3)
    else:
        query.message.reply_text("The category does not exist.")
        admin_manage_categories(update, context)

    query.answer()  # Acknowledge the callback query

#pass
def admin_list_agents(update, context):
    """Displays a list of agents and their products as separate messages with inline buttons."""
    data = load_data()  # Load the current data
    agents = data.get("agents", {})  # Get the list of agents

    if agents:
        for agent_id, agent_info in agents.items():
            agent = data["users"].get(agent_id)  # Get the agent details from user data
            if agent and agent.get('role') == 'agent':
                agent_name = agent.get('name', 'Unnamed')  # Get the agent's name
                product_ids = agent_info.get('products', [])  # Get the list of products for the agent
                product_count = len(product_ids)

                # Main inline button for the agent, including product count
                keyboard = [
                    [InlineKeyboardButton(f"Manage Agent", callback_data=f'admin_manage_agent_{agent_id}')],
                    [InlineKeyboardButton(f"↓↓ Products: {product_count} ↓↓", callback_data=f'view_agent_{agent_id}')]
                ]

                # Add buttons for each product the agent has
                if product_count > 0:
                    for product_id in product_ids:
                        product_info = data["products"].get(str(product_id))  # Get product details
                        if product_info:
                            product_name = product_info.get('name', 'Unnamed')  # Get product name

                            # Add an inline button for each product
                            keyboard.append([InlineKeyboardButton(f"📦 {product_name}", callback_data=f'admin_manage_single_product_{agent_id}_{product_id}')])
                else:
                    keyboard.append([InlineKeyboardButton("This agent has not added any products yet.", callback_data='no_action')])

                # Add a back button to the main menu for each agent
                keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data='admin_menu')])

                reply_markup = InlineKeyboardMarkup(keyboard)  # Create the inline keyboard markup

                # Message for each agent
                message = f"👤 Agent: {agent_name} (ID: {agent_id})"

                # Send a separate message for each agent
                if update.callback_query:
                    # update.callback_query.message.delete()  # Optionally delete the previous message
                    update.callback_query.message.reply_text(message, reply_markup=reply_markup)
                    update.callback_query.answer()
                else:
                    update.message.reply_text(message, reply_markup=reply_markup)
    else:
        # If there are no agents, notify the user
        if update.message:
            update.message.reply_text("No agents found.")
        elif update.callback_query:
            update.callback_query.message.reply_text("No agents found.")
            update.callback_query.answer()

#pass
def admin_manage_agent(update, context):
    """Manages agent details, including deletion and report generation."""
    query = update.callback_query
    data = query.data  # Retrieve callback query data
    agent_id = data.split('_')[-1]  # Extract agent ID from the callback data

    data = load_data()  # Load the data
    agent = data["users"].get(agent_id)  # Get agent details

    if agent:
        agent_name = agent.get('name', 'Unnamed')  # Get agent name

        # Create buttons for agent management
        keyboard = [
            [InlineKeyboardButton("Get Full Report", callback_data=f'admin_get_report_{agent_id}')],
            [InlineKeyboardButton("Delete Agent", callback_data=f'admin_delete_agent_{agent_id}')],
            [InlineKeyboardButton("Back to Main Menu", callback_data='admin_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)  # Set up the inline keyboard

        message = f"Manage Agent {agent_name} (ID: {agent_id})"
        
        # Send the agent management message
        query.message.reply_text(message, reply_markup=reply_markup)
        query.answer()
    else:
        query.message.reply_text("The agent could not be found.")
        query.answer()

#pass
def admin_get_report(update, context):
    """Generates a report for a specific agent, including sold products and total sales value."""
    query = update.callback_query
    data = query.data  # Retrieve callback query data
    agent_id = data.split('_')[-1]  # Extract agent ID from callback data

    data = load_data()  # Load the data
    agent = data["users"].get(agent_id)  # Get agent details
    products = data.get("products", {})  # Get the list of products

    if not agent:
        query.message.reply_text("The agent could not be found.")
        query.answer()
        return

    agent_name = agent.get('name', 'Unnamed')  # Get agent name
    total_sales_value = 0
    sold_products_report = ""

    # Loop through the agent's products and gather sales information
    for product_id in agent.get('products', []):
        product_info = products.get(str(product_id))

        if product_info:
            product_name = product_info.get('name', 'Unknown')  # Get product name
            product_price = product_info.get('price', 0)  # Get product price
            sold_quantity = product_info.get('sold', 0)  # Get quantity sold

            # Only include products that have been sold
            if sold_quantity > 0:
                sales_value = product_price * sold_quantity  # Calculate total sales for the product
                total_sales_value += sales_value  # Add to total sales value

                # Append product details to the report
                sold_products_report += (
                    f"Product Name: {product_name}\n"
                    f"Price: {product_price if product_price else 'Unknown'}\n"
                    f"Sold Quantity: {sold_quantity}\n"
                    f"Total Sales: {sales_value}\n"
                    "-----------------------------\n"
                )

    # Final report message
    report_message = (
        f"Agent Report: {agent_name}\n (ID: {agent_id})\n\n"
        f"Total Sales Value: {total_sales_value}\n"
        "-----------------------------\n"
        f"Sold Products Report:\n"
        f"{sold_products_report if sold_products_report else 'No products have been sold.'}\n"
    )

    # Send the report message
    query.message.reply_text(report_message)
    query.answer()

#pass
def admin_delete_agent(update, context):
    """Remove an agent from the list and update the data."""
    query = update.callback_query
    data = query.data  # Retrieve callback data
    agent_id = data.split('_')[-1]  # Extract agent_id from callback_data

    # Load data from the JSON file
    data = load_data()

    # Check if the agent exists
    agent = data["users"].get(agent_id)
    
    if agent and agent.get('role') == 'agent':
        # Find the agent's products
        products_to_delete = data["agents"].get(agent_id, {}).get("products", [])
        
        # Remove products from the product list
        for product_id in products_to_delete:
            if str(product_id) in data["products"]:
                del data["products"][str(product_id)]  # Delete product from the products dictionary

        # Remove the agent from the users list
        del data["users"][agent_id]
        
        # Remove the agent from the agents list
        if agent_id in data["agents"]:
            del data["agents"][agent_id]

        save_data(data)  # Save changes to the JSON file
        query.message.reply_text(f"Agent '{agent.get('name', 'Unnamed')}' and their associated products were successfully deleted.")
    else:
        query.message.reply_text("The agent was not found or has already been deleted.")

    query.answer()

#pass
def admin_manage_single_product(update, context):
    """Display information about a specific product and management options."""
    data = update.callback_query.data  # Retrieve callback data
    parts = data.split('_')  # Split the data into parts
    if len(parts) < 3:
        update.callback_query.message.reply_text("Insufficient data for managing the product.")
        update.callback_query.answer()
        return
    
    agent_id = parts[4]  # Extract agent_id
    product_id = parts[5]  # Extract product_id
    data = load_data()
    
    # Find the product by product ID
    product_info = data["products"].get(str(product_id))
    agent = data["users"].get(agent_id)

    if product_info and agent:
        agent_name = agent.get('name', 'Unnamed')
        product_name = product_info.get('name', 'Unnamed')
        price = product_info.get('price', 'No price')
        stock = product_info.get('stock', 'No stock')
        product_city = product_info.get('city', 'No city')
        category = product_info.get('category', 'No category')

        # Product message with complete details
        product_message = (
            f"📦 Product Name: {product_name}\n"
            f"Price: {price} Toman\n"
            f"City: {product_city}\n"
            f"Stock: {stock}\n"
            f"Agent: {agent_name}\n"
            f"Category: {category}\n"
        )

        # Create inline buttons for editing and deleting
        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=f"admin_edit_product_{agent_id}_{product_id}"),
                InlineKeyboardButton("Delete", callback_data=f"admin_delete_product_{product_id}")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_list_agents")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the product message
        if update.callback_query:
            update.callback_query.message.delete()
            update.callback_query.message.reply_text(product_message, reply_markup=reply_markup)
            update.callback_query.answer()
    else:
        if update.callback_query:
            update.callback_query.message.reply_text("The product was not found or the agent is invalid.")
            update.callback_query.answer()

#pass
def admin_delete_product(update, context):
    """Delete a product by the admin."""
    query_data = update.callback_query.data.split('_')
    product_id = query_data[3]  # Extract product_id
    data = load_data()
    product_info = data["products"].get(product_id)

    if product_info:
        agent_id = product_info['agent_id']  # Extract agent_id from product info
        agent_info = data["agents"].get(agent_id)

        # Remove the product from the agent's product list
        if agent_info and int(product_id) in agent_info['products']:  # Convert to int for consistency
            agent_info['products'].remove(int(product_id))  # Remove product ID from the agent's list
            del data["products"][product_id]  # Delete the product from the database
            save_data(data)  # Save changes to the file

            update.callback_query.message.reply_text(f"The product {product_info['name']} was successfully deleted.")
        else:
            update.callback_query.message.reply_text("The product was not found in the agent's list.")
    else:
        update.callback_query.message.reply_text("The product was not found.")

    update.callback_query.answer()

#soon
def admin_edit_product(update, context):
    """Edit a product by the admin."""
    update.callback_query.message.reply_text("This feature will be added in the next update.")
    update.callback_query.answer()

#pass
def admin_add_agent_start(update, context):
    """Start the process of adding an agent by requesting the new agent's numeric ID, with a cancel button."""
    keyboard = [[InlineKeyboardButton("Cancel", callback_data='admin_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text("Please enter the new agent's numeric ID:", reply_markup=reply_markup)
    update.callback_query.answer()

    # Save the stage to receive the agent's ID
    context.user_data['adding_agent'] = True

#pass
def admin_add_agent(update, context):
    """Add a new agent to the database."""
    if 'adding_agent' in context.user_data and context.user_data['adding_agent']:
        agent_id = update.message.text.strip()  # Get the agent ID from the user's input

        # Check if the ID is numeric
        if agent_id.isdigit():
            agent_id = str(agent_id)  # Convert to string for saving in the database

            # Load data from the file
            data = load_data()

            # Check if an agent with this ID already exists
            if agent_id not in data['agents']:
                # Add the agent to the database
                data['users'][agent_id] = {
                    "role": "agent",
                    "balance": 0,
                    "city": "",
                    "cart": {},
                    "orders": []
                }

                # Also add the agent to the agents list
                data['agents'][agent_id] = {
                    "products": []  # The agent's product list is currently empty
                }

                # Save the changes
                save_data(data)

                update.message.reply_text(f"Agent with ID {agent_id} was successfully added.")
                admin_menu(update, context)
            else:
                keyboard = [[InlineKeyboardButton("Cancel", callback_data='admin_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("This agent ID already exists. Please enter another ID.", reply_markup=reply_markup)
                
        else:
            keyboard = [[InlineKeyboardButton("Cancel", callback_data='admin_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Please enter a valid numeric ID.", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("Cancel", callback_data='admin_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("The agent adding process has not started yet.", reply_markup=reply_markup)

#pass
def admin_report(update, context):
    """Generate a report for admin including total users, agents, sold products, and total sales value."""
    data = load_data()  # Load data from JSON file

    # Calculate the number of users and agents
    users = data.get('users', {})
    agents = data.get('agents', {})
    total_users = len(users)
    total_agents = len(agents)

    # Report on sold products and total sales value
    products = data.get('products', {})
    total_sales_value = 0
    sold_products_report = ""

    for product_id, product_info in products.items():
        product_name = product_info.get('name', 'Unnamed')
        product_price = product_info.get('price', 0)
        sold_quantity = product_info.get('sold', 0)

        # Only include products with sold quantity greater than 0
        if sold_quantity > 0:
            # Ensure price is not None before calculation
            if product_price is not None:
                sales_value = product_price * sold_quantity
            else:
                sales_value = 0

            total_sales_value += sales_value

            # Append product sales details to the report
            sold_products_report += (
                f"Product Name: {product_name}\n"
                f"Price: {product_price if product_price else 'Unknown'} Toman\n"
                f"Sold Quantity: {sold_quantity}\n"
                f"Sales Amount: {sales_value} Toman\n"
                "-----------------------------\n"
            )

    # Construct the final report message
    report_message = (
        f"📊 Total Report 📊\n\n"
        f"Total Users: {total_users}\n"
        f"Total Agents: {total_agents}\n\n"
        f"Total Sales Amount: {total_sales_value} Toman\n"
        "-----------------------------\n"
        f"Sold Products Report:\n"
        f"{sold_products_report if sold_products_report else 'No products sold.'}\n"
    )

    # Check if update.message is available before replying
    if update.message:
        update.message.reply_text(report_message)
    else:
        update.callback_query.message.reply_text(report_message)
        update.callback_query.answer()
