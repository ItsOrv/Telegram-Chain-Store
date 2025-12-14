# Telegram Chain Store

A decentralized e-commerce Telegram bot with role-based access control, secure payment processing, and location-based delivery management.

## Overview

Telegram Chain Store is a comprehensive marketplace bot built on the Telegram platform. It provides a secure, multi-role system for managing product sales, payments, and deliveries with built-in verification mechanisms and location-based coordination.

## Features

### Role-Based Access Control

- **Buyer**: Browse products, manage cart, place orders, and make payments through wallet or direct payment methods
- **Seller**: Add and manage products, handle initial payment verification, and coordinate deliveries at assigned locations
- **Cardholder**: Verify payments and wallet top-ups, manage payment method distribution for payouts
- **Admin**: Final payment approval, location management, user administration, and system-wide control

### Payment System

- Two-step payment verification (Cardholder → Admin)
- Multiple payment methods: wallet balance, direct payment, cryptocurrency
- Secure wallet management with transaction history
- Payment gateway integration support
- Automatic payment timeout handling

### Delivery Management

- Location-based delivery system with city-level organization
- Secure drop-off location assignment
- Time-delayed location disclosure (15 minutes after drop-off)
- Delivery code validation for order confirmation
- Address expiry management

### Security

- Role-based permission system
- Two-factor payment verification
- Input validation and sanitization
- Rate limiting and request throttling
- Secure token management
- Comprehensive logging and error handling

## Technology Stack

- **Framework**: Python 3.12+
- **Telegram Library**: Telethon 1.34.0
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Cache**: Redis 5.0.1
- **Migrations**: Alembic
- **Configuration**: Pydantic Settings
- **Security**: python-jose, passlib, cryptography

## Prerequisites

- Python 3.12 or higher
- MySQL 8.0 or compatible database
- Redis server
- Telegram Bot Token and API credentials

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd Telegram-Chain-Store
```

2. Create and activate virtual environment:
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
# Edit .env with your configuration
```

Required environment variables:
- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API Hash
- `BOT_TOKEN`: Telegram Bot Token
- `BOT_USERNAME`: Bot username
- `HEAD_ADMIN_ID`: Admin user ID
- `SUPPORT_ID`: Support user ID
- `SUPPORT_USERNAME`: Support username
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `SECRET_KEY`: Application secret key
- `CRYPTO_WALLET_ADDRESS`: Cryptocurrency wallet address

5. Initialize database:
```bash
alembic upgrade head
```

6. Run the application:
```bash
python -m src.main
```

### Docker Deployment

1. Configure environment variables in `.env` file

2. Build and start services:
```bash
docker-compose up --build -d
```

3. Run database migrations:
```bash
docker exec -it telegram-chain-store-bot alembic upgrade head
```

4. View logs:
```bash
docker-compose logs -f telegram-bot
```

## Configuration

The application uses Pydantic Settings for configuration management. All settings are loaded from environment variables or a `.env` file in the project root.

Key configuration categories:
- **App Settings**: Debug mode, logging level
- **Telegram Settings**: API credentials, bot configuration
- **Database Settings**: Connection parameters, pool configuration
- **Redis Settings**: Cache and session management
- **Security Settings**: Secret keys, token expiration
- **Crypto Settings**: Wallet address, network, payment timeout

## Project Structure

```
Telegram-Chain-Store/
├── src/
│   ├── bot/              # Bot handlers and client
│   │   ├── handlers/     # Message and callback handlers
│   │   ├── keyboards/    # Inline keyboard definitions
│   │   └── utils/        # Bot utilities
│   ├── config/           # Configuration management
│   ├── core/             # Core business logic
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic services
│   │   └── repositories/ # Data access layer
│   ├── integrations/     # External service integrations
│   │   ├── delivery/     # Delivery service integration
│   │   ├── notifications/# Notification services
│   │   └── payment/      # Payment gateway integrations
│   └── utils/            # Utility functions
├── migrations/           # Database migration scripts
├── scripts/              # Setup and utility scripts
├── translations/         # Localization files
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Container definition
└── requirements.txt     # Python dependencies
```

## Development

### Code Style

The project uses:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting

Run formatting:
```bash
black src/
isort src/
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

### Testing

Run tests:
```bash
pytest
```

## License

[Specify license if applicable]
