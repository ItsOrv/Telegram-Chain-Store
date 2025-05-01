# Telegram Chain Store Bot

این ربات تلگرام یک فروشگاه زنجیره‌ای با قابلیت‌های پرداخت، مدیریت محصولات و سیستم تحویل مبتنی بر مکان می‌باشد.

## ساختار پروژه

ساختار اصلی پروژه به شرح زیر است:

```
src/
├── bot/                   # کد مربوط به ربات تلگرام
│   ├── keyboards/         # کیبوردهای تمام بخش‌ها
│   ├── handlers/          # هندلرهای کالبک و دستورات
│   │   ├── callback_router.py  # مسیردهی کالبک‌ها
│   │   ├── admin_callbacks.py  # کالبک‌های مدیر
│   │   ├── user_callbacks.py   # کالبک‌های کاربر
│   │   └── ...
│   ├── utils/             # ابزارهای کمکی
│   ├── common/            # عناصر مشترک (پیام‌ها، ثابت‌ها)
│   ├── setup.py           # راه‌اندازی ربات
│   └── client.py          # کلاینت اصلی ربات
├── core/                  # هسته اصلی برنامه
│   ├── models/            # مدل‌های داده
│   ├── services/          # سرویس‌های مختلف
│   └── database.py        # پیکربندی پایگاه داده
├── config/                # تنظیمات برنامه
├── utils/                 # ابزارهای عمومی
└── integrations/          # ادغام با سرویس‌های خارجی
```

## بخش‌های اصلی

### Bot Handlers

فایل‌های `*_callbacks.py` منطق اصلی کالبک‌های برنامه را پیاده‌سازی می‌کنند. هر فایل مسئول یک بخش خاص از برنامه است:

- `admin_callbacks.py`: کالبک‌های مربوط به پنل مدیریت
- `user_callbacks.py`: کالبک‌های مربوط به کاربران
- `product_callbacks.py`: کالبک‌های مربوط به محصولات
- `payment_callbacks.py`: کالبک‌های مربوط به پرداخت‌ها
- `order_callbacks.py`: کالبک‌های مربوط به سفارش‌ها
- `cart_callbacks.py`: کالبک‌های مربوط به سبد خرید

### Bot Keyboards

کیبوردهای استفاده شده در برنامه در پوشه `keyboards` قرار دارند و شامل:

- `admin_keyboard.py`: کیبوردهای پنل مدیریت
- `user_keyboard.py`: کیبوردهای کاربران
- `product_keyboard.py`: کیبوردهای محصولات
- `payment_keyboard.py`: کیبوردهای پرداخت
- `main_keyboard.py`: کیبوردهای اصلی برنامه

## نحوه راه‌اندازی

1. فایل `.env` را با تنظیمات مورد نیاز پیکربندی کنید
2. وابستگی‌ها را نصب کنید:
   ```bash
   pip install -r requirements.txt
   ```
3. پایگاه داده را راه‌اندازی کنید:
   ```bash
   python -m src.core.database
   ```
4. ربات را اجرا کنید:
   ```bash
   python -m src.main
   ```

## راهنمای ساختار کد

### افزودن هندلر جدید

برای افزودن یک هندلر جدید، یک تابع با دکوراتور `register_callback` در فایل مربوطه ایجاد کنید:

```python
@register_callback("action_name")
async def handle_action(event: events.CallbackQuery.Event, params: List[str]) -> None:
    """Handle action callback"""
    # Your code here
```

### افزودن کیبورد جدید

برای افزودن یک کیبورد جدید، یک تابع در فایل مربوطه در پوشه `keyboards` ایجاد کنید:

```python
def get_new_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for new action
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("Button 1", "action:param1"),
            Button.inline("Button 2", "action:param2")
        ],
        [
            Button.inline("« بازگشت", "navigation:main_menu")
        ]
    ]
```

## Features

### Role-Based System
- **Buyer**: Browse and purchase products, pay via wallet or direct payment
- **Seller**: List products, receive drop-off locations, manage orders
- **Cardholder**: Manually verify payments and wallet top-ups
- **Admin**: Final approval of payments, manage locations and users

### Secure Two-Step Payment Process
1. Payment is made by buyer
2. Cardholder verifies the payment
3. Admin confirms the payment
4. Funds are released

### Location-Based Delivery System
- Admin defines safe public locations per city/area
- Sellers drop products at designated locations
- Buyers receive location details 15 minutes after drop-off
- Delivery code verification ensures security

### Wallet System
- Users can recharge their wallet
- Two-step verification for all wallet transactions
- Secure balance management

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL/MariaDB
- Redis (for caching and session management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-chain-store.git
cd telegram-chain-store
```

2. Create a virtual environment:
   ```bash
   python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
# Edit .env with your settings
```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the bot:
   ```bash
python -m src.main
```

## Security Features

- Manual two-step payment verification
- Delivery code verification
- User role validation and access control
- Input validation and sanitization
- Error handling and logging
- Rate limiting for API requests

## Development

### Adding New Features

1. Create appropriate models in `src/core/models/`
2. Implement business logic in `src/core/services/`
3. Create handlers in `src/bot/handlers/`
4. Register handlers in `src/bot/common/handlers.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.


