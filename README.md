# Stock Reminder App

A Python web application that monitors your stock portfolio and sends email alerts when any stock drops more than 5% in a day.

## Features

- Add/remove stocks to monitor
- Automatic hourly price checks
- Email alerts when stocks drop >5%
- Web dashboard to view current prices and recent alerts
- Google Sheets dashboard integration (shareable with family)
- CSV import for bulk stock additions
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

### 3. (Optional) Configure Google Sheets Integration

To sync data to a shareable Google Sheets dashboard:

1. Enable Google Sheets API and Google Drive API in Google Cloud Console
2. Create a Service Account and download credentials JSON
3. Save as `credentials.json` in project directory
4. Create a Google Sheet called "Stock Reminder Dashboard"
5. Share it with your service account email (found in credentials.json)

### 4. Run the Application

```bash
python app.py
```

The app will run at `http://localhost:5001`

## Usage

### Web Dashboard
1. Open `http://localhost:5001` in your browser
2. Add stock ticker symbols (e.g., AAPL, TSLA, GOOGL)
3. The app will check prices every hour
4. You'll receive email alerts when stocks drop >5%
5. Click "Check All Now" to manually trigger a check

### CSV Import
Import multiple stocks at once:
```bash
python import_stocks.py
```
Edit `positions.csv` with your stock list (Ticker, Description, Brokerage columns)

### Google Sheets Sync
Update your shareable Google Sheets dashboard:
```bash
python sheets_sync.py
```

## How It Works

- Checks stock prices every hour
- Compares today's closing price to previous day's closing price
- Sends email alert if daily drop exceeds 5%
- Only one alert per stock per day to avoid spam
- Uses Yahoo Finance for real-time stock data
- Syncs to Google Sheets for shareable dashboard

## Files

- `app.py` - Flask web application
- `stock_monitor.py` - Stock checking and email alerts
- `sheets_sync.py` - Google Sheets dashboard sync
- `import_stocks.py` - CSV import utility
- `database.py` - SQLite database operations
- `templates/index.html` - Web interface
- `positions.csv` - Your stock list (not tracked in git)
- `stocks.db` - SQLite database (created automatically)
- `credentials.json` - Google API credentials (not tracked in git)

## Notes

- Market hours are typically 9:30 AM - 4:00 PM ET
- The app checks prices 24/7, but only market hour data is relevant
- Stock data is provided by Yahoo Finance (free, no API key needed)
