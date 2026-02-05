import gspread
from google.oauth2.service_account import Credentials
import yfinance as yf
from datetime import datetime
from database import get_all_stocks, get_recent_alerts
from dotenv import load_dotenv
import os

load_dotenv()

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheets_client():
    """Get authenticated Google Sheets client."""
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return gspread.authorize(creds)

def create_or_open_spreadsheet(client, sheet_name="Stock Reminder Dashboard"):
    """Create a new spreadsheet or open existing one."""
    try:
        # Try to open existing spreadsheet
        spreadsheet = client.open(sheet_name)
        print(f"✓ Opened existing spreadsheet: {sheet_name}")
    except gspread.SpreadsheetNotFound:
        # Create new spreadsheet
        spreadsheet = client.create(sheet_name)
        print(f"✓ Created new spreadsheet: {sheet_name}")

        # Move to "Stock Reminder App" folder if it exists
        # Note: You'll need to share the folder with the service account email

    return spreadsheet

def update_stocks_sheet(spreadsheet):
    """Update the stocks data in the spreadsheet."""
    # Get or create "Stocks" worksheet
    try:
        worksheet = spreadsheet.worksheet("Stocks")
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Stocks", rows=100, cols=10)

    # Get stock data
    stocks = get_all_stocks()

    # Prepare data
    data = [
        ["Stock Reminder Dashboard", "", "", "", f"Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"],
        [],
        ["Ticker", "Current Price", "Today's Change", "Change %", "Added Date", "Status"]
    ]

    drop_threshold = float(os.getenv('DROP_THRESHOLD', 5.0))

    for stock_id, ticker, added_date in stocks:
        try:
            stock = yf.Ticker(ticker)
            stock_data = stock.history(period='5d')

            if not stock_data.empty and len(stock_data) >= 2:
                current_price = stock_data['Close'].iloc[-1]
                previous_close = stock_data['Close'].iloc[-2]
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100

                status = "🚨 ALERT" if change_percent <= -drop_threshold else "✓ OK"

                data.append([
                    ticker,
                    f"${current_price:.2f}",
                    f"${change:+.2f}",
                    f"{change_percent:+.2f}%",
                    added_date[:10],
                    status
                ])
            else:
                data.append([ticker, "N/A", "N/A", "N/A", added_date[:10], "⚠ No Data"])
        except Exception as e:
            data.append([ticker, "ERROR", "ERROR", "ERROR", added_date[:10], f"⚠ {str(e)[:20]}"])

    # Write data to sheet
    worksheet.update(values=data, range_name='A1')

    # Format the sheet
    format_stocks_sheet(worksheet, len(data))

    print(f"✓ Updated {len(stocks)} stocks in spreadsheet")
    return worksheet

def format_stocks_sheet(worksheet, num_rows):
    """Apply formatting to make the sheet look like a dashboard."""
    # Header row formatting (row 3)
    worksheet.format('A3:F3', {
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'horizontalAlignment': 'CENTER'
    })

    # Title formatting (row 1)
    worksheet.format('A1:E1', {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'LEFT'
    })

    # Freeze header rows
    worksheet.freeze(rows=3)

    # Note: Column widths can be adjusted manually in Google Sheets

    print("✓ Applied formatting to spreadsheet")

def update_alerts_sheet(spreadsheet):
    """Update the alerts history in the spreadsheet."""
    try:
        worksheet = spreadsheet.worksheet("Alerts")
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Alerts", rows=100, cols=5)

    alerts = get_recent_alerts(100)

    data = [
        ["Recent Alerts", "", "", ""],
        [],
        ["Ticker", "Drop %", "Price", "Date/Time"]
    ]

    for alert in alerts:
        ticker, drop_pct, alert_date, price = alert
        data.append([
            ticker,
            f"-{drop_pct:.2f}%",
            f"${price:.2f}",
            alert_date[:19]
        ])

    worksheet.update(values=data, range_name='A1')

    # Format header
    worksheet.format('A3:D3', {
        'backgroundColor': {'red': 0.8, 'green': 0.3, 'blue': 0.3},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'horizontalAlignment': 'CENTER'
    })

    worksheet.freeze(rows=3)

    print(f"✓ Updated {len(alerts)} alerts in spreadsheet")

def sync_to_sheets():
    """Main function to sync all data to Google Sheets."""
    print("\n" + "="*50)
    print("Syncing to Google Sheets...")
    print("="*50 + "\n")

    try:
        # Connect to Google Sheets
        client = get_sheets_client()

        # Create or open spreadsheet
        spreadsheet = create_or_open_spreadsheet(client)

        # Update sheets
        update_stocks_sheet(spreadsheet)
        update_alerts_sheet(spreadsheet)

        print(f"\n✅ Successfully synced to Google Sheets!")
        print(f"📊 View your dashboard: {spreadsheet.url}")

        return spreadsheet.url

    except Exception as e:
        print(f"❌ Error syncing to Google Sheets: {str(e)}")
        return None

if __name__ == '__main__':
    sync_to_sheets()
