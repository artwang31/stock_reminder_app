# Stock Reminder App

A Python web application that monitors your stock portfolio and sends email alerts when any stock drops more than 5% in a day.

## Features

- Add/remove stocks to monitor
- Automatic hourly price checks
- Email alerts when stocks drop >5%
- Web dashboard to view current prices and recent alerts
- One alert per stock per day (no spam)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and configure your email settings:

```env
# For Gmail users:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com

# Alert settings
DROP_THRESHOLD=5.0
CHECK_INTERVAL_MINUTES=60
```

### Gmail Setup

If using Gmail, you need to create an **App Password**:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security > 2-Step Verification > App passwords
4. Generate a new app password for "Mail"
5. Use this password in your `.env` file

### 3. Run the Application

```bash
python app.py
```

The app will run at `http://localhost:5000`

## Usage

1. Open `http://localhost:5000` in your browser
2. Add stock ticker symbols (e.g., AAPL, TSLA, GOOGL)
3. The app will check prices every hour
4. You'll receive email alerts when stocks drop >5%
5. Click "Check All Now" to manually trigger a check

## How It Works

- Checks stock prices every hour during the day
- Compares current price to the day's opening price
- Sends email alert if drop exceeds 5%
- Only one alert per stock per day to avoid spam
- Uses Yahoo Finance for real-time stock data

## Files

- `app.py` - Flask web application
- `stock_monitor.py` - Stock checking and email alerts
- `database.py` - SQLite database operations
- `templates/index.html` - Web interface
- `stocks.db` - SQLite database (created automatically)

## Notes

- Market hours are typically 9:30 AM - 4:00 PM ET
- The app checks prices 24/7, but only market hour data is relevant
- Stock data is provided by Yahoo Finance (free, no API key needed)
