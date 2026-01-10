# ✈️ TripSplitter Bot

**TripSplitter** is a smart Telegram bot designed to help groups of travelers track expenses and split bills effortlessly. It supports multi-currency expenses, automatic conversion to the base currency (KZT), and debt minimization algorithms.

## 🚀 Features

* **Smart Expense Tracking:** Add expenses with a simple command (`/paid 5000 taxi`).
* **Currency Conversion:** Automatically converts foreign currencies (USD, EUR, GBP, etc.) to KZT using **Yahoo Finance API**.
* **Debt Minimization:** Calculates the most efficient way to settle debts between participants.
* **Multi-Language Support:** Full support for English, Russian, and Kazakh languages (`/lang`).
* **Persistent Storage:** All data is securely stored in a **PostgreSQL** database.
* **User Management:** Supports excluding specific users from a bill (`except @user`) and adding non-paying participants (`/join`).

## 🛠 Tech Stack

* **Language:** Python 3.12
* **Framework:** Aiogram 3 (Asynchronous)
* **Database:** PostgreSQL 16
* **ORM:** SQLAlchemy (AsyncPG)
* **External APIs:** Yahoo Finance (via `yfinance`)

## ⚙️ Installation & Setup

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/TripSplitter.git](https://github.com/YOUR_USERNAME/TripSplitter.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a PostgreSQL database:
    * Open **pgAdmin4** (or any SQL client).
    * Create a new database named `trip_splitter_db`.
    * (The tables will be created automatically when you run the bot).
    ```
4.  Create a `.env` file and add your credentials:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    DB_PASS=your_database_password
    ```
5.  Run the bot:
    ```bash
    python bot.py
    ```

