# QR Code-Driven URLs Project

## Overview
QR Code-Driven URLs is a platform where users can generate, purchase, and manage URLs linked to QR codes. Users can add URLs to a cart, make payments through Stripe, and receive QR codes for their purchased links.

## Features
- Generate QR codes for URLs
- Add URLs to a cart
- Secure checkout and payments via Stripe
- URL ownership tracking
- Email notifications for purchases
- Admin panel for managing users and transactions

## Installation Guide

### Prerequisites

Programming Language: Python
Framework: Django (Web Framework)
Database: PostgreSQL (PSQL)
Payment Integration: Stripe

### Clone the Repository
```sh
git clone https://github.com/sruthisreya/ecommerce-qrcode-project.git
cd ecommerce-qrcode-project
```

### Setup Virtual Environment (Windows)
```sh
python -m venv env
env\Scripts\activate

-Linux/Mac:
source venv/bin/activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```
### Configure Environment Variables (.env)

Create a .env file in the root directory and add the following:

DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/your_db_name
STRIPE_PUBLIC_KEY=your_public_key
STRIPE_SECRET_KEY=your_secret_key

### Configure Database
Update the `.env` file or `settings.py` with your database credentials.

Run migrations:
```sh
python manage.py migrate
```

### Configure Stripe Payment Gateway
1. Create a Stripe account at [https://stripe.com]
2. Get your API keys from the Stripe dashboard
3. Update your `.env` file with:
   ```
   STRIPE_PUBLIC_KEY=your_public_key
   STRIPE_SECRET_KEY=your_secret_key
   ```
4. Ensure Stripe is integrated in the payment flow in `views.py`.

### Create a Superuser (for Admin Access)
```sh
python manage.py createsuperuser
```

### Run the Development Server
```sh
python manage.py runserver
```
Access the app at `http://127.0.0.1:8000/`

## Deployment Guide

### Server Requirements
- Windows Server or Ubuntu 20.04 or later
- PostgreSQL Database
### Additional Notes
Always keep your dependencies updated and check for security vulnerabilities.Regularly back up your database and static files.



