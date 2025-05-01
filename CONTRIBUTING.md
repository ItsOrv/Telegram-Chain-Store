# راهنمای مشارکت در پروژه

از علاقه شما به مشارکت در این پروژه متشکریم. این سند راهنمایی‌هایی برای مشارکت در کد این پروژه را ارائه می‌دهد.

## گردش کار توسعه

1. یک issue انتخاب کنید یا یک issue جدید ایجاد کنید که مشکل یا قابلیت موردنظر شما را توصیف می‌کند.
2. یک branch جدید از شاخه `main` ایجاد کنید:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. تغییرات خود را اعمال کنید و کد را به صورت مرتب نگه دارید.
4. تست‌های مناسب بنویسید که تغییرات شما را پوشش دهد.
5. اطمینان حاصل کنید که کد شما با استانداردهای کدنویسی پروژه مطابقت دارد:
   ```bash
   # فرمت‌دهی کد
   black .
   
   # مرتب‌سازی import‌ها
   isort .
   
   # بررسی خطاها
   flake8
   ```
6. تغییرات خود را commit کنید:
   ```bash
   git commit -m "توضیح مختصر در مورد تغییرات"
   ```
7. تغییرات خود را به repository خود push کنید:
   ```bash
   git push origin feature/your-feature-name
   ```
8. یک Pull Request به شاخه `main` ارسال کنید.

## استانداردهای کدنویسی

- از PEP 8 پیروی کنید
- docstring برای همه توابع و کلاس‌ها بنویسید
- type hints استفاده کنید
- تست بنویسید که تمام تغییرات کد را پوشش دهد
- نام‌گذاری‌ها باید واضح و معنادار باشند

## ساختار پوشه‌ها

برای افزودن قابلیت‌های جدید، لطفاً ساختار پوشه‌بندی موجود را دنبال کنید:

- `src/bot/handlers/`: هندلرهای کالبک و دستورات
- `src/bot/keyboards/`: کیبوردهای تعاملی
- `src/core/models/`: مدل‌های داده
- `src/core/services/`: سرویس‌های تجاری
- `src/integrations/`: ادغام با سرویس‌های خارجی

## افزودن هندلر جدید

برای اضافه کردن هندلر جدید، لطفاً الگوی موجود را دنبال کنید:

```python
from telethon import events
from src.bot.handlers.callback_router import register_callback

@register_callback("action_name")
async def handle_action(event: events.CallbackQuery.Event, params: list) -> None:
    """
    توضیح عملکرد هندلر
    
    Args:
        event: رویداد کالبک تلگرام
        params: پارامترهای استخراج شده از داده‌های کالبک
    """
    # پیاده‌سازی هندلر
```

## افزودن کیبورد جدید

برای اضافه کردن کیبورد جدید، لطفاً الگوی موجود را دنبال کنید:

```python
from telethon import Button
from typing import List

def get_new_keyboard() -> List[List[Button]]:
    """
    ایجاد کیبورد برای عملیات جدید
    
    Returns:
        لیستی از ردیف‌های دکمه
    """
    return [
        [
            Button.inline("دکمه 1", "action:param1"),
            Button.inline("دکمه 2", "action:param2")
        ],
        [
            Button.inline("« بازگشت", "navigation:main_menu")
        ]
    ]
```

## گزارش مشکلات

لطفاً مشکلات را با جزئیات کافی گزارش دهید تا بتوانیم آن‌ها را بازتولید کنیم. شامل:

- اقدامات دقیق برای بازتولید مشکل
- خروجی خطا و لاگ‌ها
- محیط اجرایی (سیستم عامل، نسخه پایتون، و غیره)

## سؤالات

اگر سؤالی دارید، لطفاً یک issue با برچسب "question" ایجاد کنید.

با تشکر از مشارکت شما! 