import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from database import get_all_stocks, log_alert, was_alert_sent_today

def check_stocks():
    """Check all stocks for price drops."""
    stocks = get_all_stocks()
    drop_threshold = float(os.getenv('DROP_THRESHOLD', 5.0))

    print(f"[{datetime.now()}] Checking {len(stocks)} stocks...")

    alerts_to_send = []

    for stock_id, ticker, added_date in stocks:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='5d')

            if data.empty or len(data) < 2:
                print(f"  {ticker}: No data available")
                continue

            current_price = data['Close'].iloc[-1]
            previous_close = data['Close'].iloc[-2]

            change_percent = ((current_price - previous_close) / previous_close) * 100

            print(f"  {ticker}: ${current_price:.2f} ({change_percent:+.2f}%)")

            if change_percent <= -drop_threshold:
                if not was_alert_sent_today(ticker):
                    alerts_to_send.append({
                        'ticker': ticker,
                        'current_price': current_price,
                        'drop_percentage': abs(change_percent)
                    })
                    log_alert(ticker, abs(change_percent), current_price)
                    print(f"  ⚠️  ALERT: {ticker} dropped {abs(change_percent):.2f}%!")
                else:
                    print(f"  ℹ️  {ticker} dropped {abs(change_percent):.2f}% (alert already sent today)")

        except Exception as e:
            print(f"  {ticker}: Error - {str(e)}")

    if alerts_to_send:
        send_email_alert(alerts_to_send)

    return len(alerts_to_send)

def send_email_alert(alerts):
    """Send email notification for stock alerts."""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    if not all([smtp_server, sender_email, sender_password, recipient_email]):
        print("Email configuration incomplete. Skipping email notification.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🚨 Stock Alert: {len(alerts)} stock(s) dropped >5%"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    alert_list = "\n".join([
        f"• {alert['ticker']}: ${alert['current_price']:.2f} (DOWN {alert['drop_percentage']:.2f}%)"
        for alert in alerts
    ])

    text_content = f"""Stock Price Alert

The following stocks have dropped more than 5% today:

{alert_list}

Time to buy the dip!

---
Stock Reminder App
"""

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #d32f2f;">🚨 Stock Price Alert</h2>
        <p>The following stocks have dropped more than 5% today:</p>
        <ul style="font-size: 16px;">
          {''.join([f'<li><strong>{alert["ticker"]}</strong>: ${alert["current_price"]:.2f} <span style="color: #d32f2f;">(DOWN {alert["drop_percentage"]:.2f}%)</span></li>' for alert in alerts])}
        </ul>
        <p style="font-size: 18px; color: #388e3c;"><strong>Time to buy the dip!</strong></p>
        <hr>
        <p style="color: #666; font-size: 12px;">Stock Reminder App</p>
      </body>
    </html>
    """

    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email alert sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
