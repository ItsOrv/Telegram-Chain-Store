# Telegram Secure Chain Store Bot

This Telegram bot is a multi-role chain store system featuring secure payments, location-based delivery, an internal wallet system, and support for direct crypto payments (Solana). It is designed with a focus on security, usability, and extensibility.

---

## Features

### Multi-Role System

* **Buyer**:
  Browse and purchase products, pay via wallet or direct crypto payment, contact support, track orders, and use all buyer-related features.

* **Seller**:
  Add new products, choose delivery locations (random public location + detailed secondary address with photo), confirm order drop-offs, and manage sales.

* **Cardholder**:
  Verify user payments, manage wallet top-ups, and control their own cards and funds.

* **Admin**:
  Full control over the system including user management, transaction approvals, defining delivery locations, and monitoring all system operations.

---

### Location-Based Delivery

* Admin defines secure public locations for each city/region, accessible in the bot as a list.
* For every new order, a public location is randomly selected.
* The seller drops the product at the selected location and submits the exact secondary address along with a photo of the spot.
* The buyer receives the delivery location 15 minutes after the drop-off.
* Final delivery confirmation is done via a unique security code provided to the buyer.

---

### Secure Two-Step Payment System

1. Buyer initiates the payment.
2. Cardholder verifies and approves the payment.
3. Admin gives final approval.
4. Funds are transferred to the seller.

**Direct payments via Solana are also supported with automatic verification.**

---

### Internal Wallet System

* Users can top up their wallet balance.
* All wallet-related transactions (except Solana payments) require manual two-step verification.
* Wallet balances are securely managed and auditable.

---

### Security & Access Control

* Strict role-based access control (RBAC)
* Manual verification for payments and deliveries
* Input validation and error logging
* Request rate limiting to prevent abuse
* Comprehensive logging and audit trail

---

## Installation

### Prerequisites

* Python 3.8+
* MySQL or SQLite
* Redis (for caching and session management)

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/itsorv/telegram-chain-store.git
cd telegram-chain-store

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit the .env file with your custom settings

# Run database migrations
alembic upgrade head

# Start the bot
python -m src.main
```

