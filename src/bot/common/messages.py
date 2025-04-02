class Messages:
    # Welcome Messages
    WELCOME = "Welcome to the Chain Store Bot! Please choose your role:"
    ROLE_SELECTED = "Your role has been set to: {role}"
    
    # Error Messages
    INVALID_ROLE = "Invalid role selection. Please try again."
    UNAUTHORIZED = "You are not authorized to perform this action."
    PAYMENT_FAILED = "Payment failed. Please try again."
    
    # Product Messages
    PRODUCT_ADDED = "Product added successfully!"
    PRODUCT_REMOVED = "Product removed successfully!"
    ADD_PRODUCT_NAME = "Please enter the product name:"
    ADD_PRODUCT_PRICE = "Please enter the product price (numbers only):"
    ADD_PRODUCT_DESCRIPTION = "Please enter product description:"
    ADD_PRODUCT_IMAGE = "Please send a photo of your product:"
    ADD_PRODUCT_LOCATION = "Please enter product location (city, province):"
    PRODUCT_SAVED = "Product saved successfully! ✅"
    PRODUCT_SAVE_ERROR = "Error saving product. Please try again. ❌"
    INVALID_PRICE = "Invalid price format. Please enter a number. ⚠️"
    INVALID_LOCATION = "Invalid location format. Please use: city, province"
    
    NO_CITY_SELECTED = """❌ Product location (city) has not been selected.
Please select a city for your product."""

    # Order Messages
    ORDER_CONFIRMED = "Order confirmed! Order ID: {order_id}"
    ORDER_CANCELLED = "Order cancelled."
    ORDER_STATUS = "Order status: {status}"
    
    # Payment Messages
    PAYMENT_METHODS = "Please choose a payment method:"
    PAYMENT_CONFIRMED = "Payment confirmed!"
    CRYPTO_ADDRESS = "Please send {amount} {currency} to address: {address}"
    
    # Location Messages
    SELECT_PROVINCE = "🏢 لطفاً استان خود را انتخاب کنید:"
    SELECT_CITY = "🌆 لطفاً شهر خود را انتخاب کنید:"
    LOCATION_UPDATED = "✅ موقعیت شما به {city} در استان {province} تغییر کرد"
    LOCATION_RESET = "🔄 موقعیت شما پاک شد. لطفاً استان جدید خود را انتخاب کنید"
    
    # Admin Messages
    ADD_ADDRESS = "Please enter the delivery address for {city}:"
    ADDRESS_ADDED = "Address added successfully!"
    REPORT_GENERATED = "Report generated successfully!"
    ADMIN_WELCOME = "Welcome Head Admin! You have full access to all bot features."
    
    # Cancel Messages
    OPERATION_CANCELLED = "Operation cancelled. ❌"
    RETURN_TO_MENU = "Returning to main menu..."
    
    # Database Messages
    DATABASE_BACKUP_SUCCESS = "Database backup created successfully!"
    DATABASE_BACKUP_ERROR = "Error creating database backup: {error}"
    
    # Report Messages
    REPORT_TYPE_SELECT = "Please select report type:"
    REPORT_PERIOD_SELECT = "Please select report period:"
    REPORT_GENERATING = "Generating report..."
    REPORT_ERROR = "Error generating report: {error}"
    
    # Location Management
    INVALID_CITY_PROVINCE = "Invalid city/province format. Please use: City, Province"
    NO_ADDRESSES_AVAILABLE = "No delivery addresses available in this area"
    ADDRESS_LIMIT_REACHED = "Address limit reached for this city"
    
    # Payment Status
    PAYMENT_PENDING = "⏳ Payment pending..."
    PAYMENT_RECEIVED = "✅ Payment received!"
    PAYMENT_EXPIRED = "⚠️ Payment expired"
    
    # Delivery Status
    DELIVERY_ADDRESS_ASSIGNED = "📍 Delivery address assigned"
    DELIVERY_IN_PROGRESS = "🚚 Delivery in progress"
    DELIVERY_COMPLETED = "✅ Delivery completed"
    
    # System Messages
    ERROR_OCCURRED = "❌ An error occurred. Please try again."
    WELCOME_BACK = "Welcome back {username}! You are logged in as: {role}"
    RATE_LIMIT_EXCEEDED = "⚠️ Too many requests. Please wait a moment."
    SESSION_EXPIRED = "⚠️ Your session has expired. Please /start again."
    MAINTENANCE_MODE = "🛠 Bot is under maintenance. Please try again later."
    
    # Security Messages
    SUSPICIOUS_ACTIVITY = "⚠️ Suspicious activity detected. Your account has been temporarily blocked."
    ACCOUNT_BLOCKED = "🚫 Your account has been blocked. Please contact support."
    INVALID_TOKEN = "❌ Invalid or expired token."
    
    # Category Management
    CATEGORY_LIST = "📁 Categories List:"
    CATEGORY_OPTIONS = "Category: {name}\nChoose an action:"
    ENTER_CATEGORY_NAME = "Please enter the name for the new category:"
    ENTER_NEW_CATEGORY_NAME = "Please enter the new name for this category:"
    CATEGORY_ADDED = "✅ Category added successfully!"
    CATEGORY_UPDATED = "✅ Category updated successfully!"
    CATEGORY_DELETED = "✅ Category deleted successfully!"

    # User Management
    USERS_STATS = """📊 Users Statistics:
Total Users: {total}
Active Users: {active}
Banned Users: {banned}
Suspended Users: {suspended}"""
    ENTER_USER_ID_BAN = "Enter the user ID to ban:"
    ENTER_USER_ID_UNBAN = "Enter the user ID to unban:"
    ENTER_USER_ID_SUSPEND = "Enter the user ID to suspend:"
    ENTER_USER_ID_UNSUSPEND = "Enter the user ID to unsuspend:"
    USER_NOT_FOUND = "❌ User not found"
    INVALID_USER_ID = "❌ Invalid user ID. Please enter a valid numeric ID."
    USER_STATUS_UPDATED = "✅ User {user_id} status updated to: {status}"

    # User Status Messages
    USER_BANNED = "🚫 Your account has been banned. Please contact support for more information.\nSupport: {support_username}"
    USER_SUSPENDED = "⚠️ Your account is currently suspended. This is temporary and will be lifted soon.\nSupport: {support_username}"
    ACCOUNT_INACTIVE = "⚠️ Your account is not active. Please contact support.\nSupport: {support_username}"

    # Backup Messages
    BACKUP_PROCESSING = "⏳ Creating encrypted database backup..."
    BACKUP_COMPLETED = """✅ Database backup completed successfully
    
🔒 File is encrypted for security
📄 SHA-256 Checksum: {checksum}
⏰ Timestamp: {timestamp}

❗️ Important: The decryption key will be sent in a separate message
⚠️ Store both the backup file and key securely
♻️ This backup will expire in 24 hours"""

    BACKUP_KEY = """🔑 Backup Decryption Key:
```
{key}
```
⚠️ Store this key securely. It cannot be recovered if lost."""

    BACKUP_FAILED = "❌ Failed to create database backup"
    BACKUP_RATE_LIMIT = "⚠️ Please wait 1 hour between backup requests"

    # Seller Management
    SELLERS_STATS = """📊 Sellers Statistics:
Total Sellers: {total}
Active Sellers: {active}
Total Products: {products}
Total Orders: {orders}

📝 Sellers List:"""

    SELLER_DETAILS = """👤 Seller: {username}
📊 Statistics:
- Products: {products}
- Orders: {orders}
- Status: {status}

Select an action:"""

    ENTER_SELLER_ID = "Enter the Telegram ID of the new seller:"
    SELLER_ADDED = "✅ User has been promoted to seller successfully!"
    SELLER_DELETED = "✅ Seller has been removed successfully!"
    ALREADY_SELLER = "❌ This user is already a seller!"

    # Product Management
    PRODUCT_STATS = """📊 Products Statistics:
Total Products: {total}
Active Products: {active}
Total Stock: {stock} items
Out of Stock: {out_of_stock} products

📝 Your Products List:"""

    PRODUCT_DETAILS = """🛍 Product Details:
📦 Name: {name}
💰 Price: {price}
📊 Stock: {stock}
⚖️ Weight: {weight}g
📍 Location: {city}, {province}
📁 Category: {category}
📈 Status: {status}"""

    ADD_PRODUCT_NAME = "📝 Enter product name:"
    ADD_PRODUCT_DESCRIPTION = "📄 Enter product description:"
    ADD_PRODUCT_PRICE = "💰 Enter product price (numbers only):"
    ADD_PRODUCT_STOCK = "📦 Enter product stock quantity:"
    ADD_PRODUCT_WEIGHT = "⚖️ Enter product weight in grams:"
    ADD_PRODUCT_ZONE = "📍 Enter specific zone/area within the city:"
    ADD_PRODUCT_IMAGE = "🖼 Send product image:"
    
    INVALID_NUMBER = "❌ Please enter a valid number"
    INVALID_IMAGE = "❌ Please send a valid image"
    INVALID_PROVINCE = "❌ Invalid province selected. Please try again."
    INVALID_CITY = "❌ Invalid city selected. Please try again."
    
    PRODUCT_ADDED = "✅ Product added successfully!"
    PRODUCT_UPDATED = "✅ Product updated successfully!"
    PRODUCT_DELETED = "✅ Product deleted successfully!"

    # Product Management Messages
    SELECT_CATEGORY = "📁 Please select product category:"
    INVALID_CATEGORY = "❌ Invalid category selected. Please try again."
    NO_CATEGORIES = """❌ No categories found!
The product cannot be added without a category.
Please contact an administrator to add categories first."""
    ADD_PRODUCT_CANCELLED = "❌ Product addition cancelled. Returning to main menu..."
    NO_LOCATION_SET = """❌ You haven't set your location yet!
Please set your location first using the '📍 Change My Location' button in the main menu."""

    # Product Display Messages
    SELLER_PRODUCT_DETAILS = """🛍️ Product Details:
📦 Name: {name}
📝 Description: {description}
💰 Price: {price}
📊 Stock: {stock}
📁 Category: {category}
📈 Status: {status}

Select an action:"""

    CUSTOMER_PRODUCT_DETAILS = """🛍️ {name}
📝 {description}
💰 Price: {price}
📊 Available: {stock}
📁 Category: {category}

Select quantity:"""

    ADD_PRODUCT_PROMPT = "➕ Add more products to your store:"

    # Product List Messages
    NO_LOCATION_SET = "Please set your location first to see available products in your area."
    OUT_OF_STOCK = "This product is out of stock!"
    EXCEEDS_STOCK = "Cannot add more - exceeds available stock!"
    NO_PRODUCTS_IN_CITY = "No products available in your area."
