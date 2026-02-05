from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from database import init_db, add_stock, remove_stock, get_all_stocks, get_recent_alerts
from stock_monitor import check_stocks
import yfinance as yf

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

init_db()

scheduler = BackgroundScheduler()
scheduler.start()

check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 60))
scheduler.add_job(
    func=check_stocks,
    trigger='interval',
    minutes=check_interval,
    id='stock_checker',
    replace_existing=True
)

@app.route('/')
def index():
    stocks = get_all_stocks()
    alerts = get_recent_alerts(20)

    stock_data = []
    for stock_id, ticker, added_date in stocks:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='5d')
            if not data.empty and len(data) >= 2:
                current_price = data['Close'].iloc[-1]
                previous_close = data['Close'].iloc[-2]
                change_percent = ((current_price - previous_close) / previous_close) * 100
                stock_data.append({
                    'id': stock_id,
                    'ticker': ticker,
                    'price': current_price,
                    'change_percent': change_percent,
                    'added_date': added_date
                })
            else:
                stock_data.append({
                    'id': stock_id,
                    'ticker': ticker,
                    'price': None,
                    'change_percent': None,
                    'added_date': added_date
                })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            stock_data.append({
                'id': stock_id,
                'ticker': ticker,
                'price': None,
                'change_percent': None,
                'added_date': added_date
            })

    return render_template('index.html', stocks=stock_data, alerts=alerts, check_interval=check_interval)

@app.route('/add', methods=['POST'])
def add():
    ticker = request.form.get('ticker', '').strip().upper()
    if ticker:
        if add_stock(ticker):
            flash(f'Successfully added {ticker} to monitoring list', 'success')
        else:
            flash(f'{ticker} is already in the monitoring list', 'warning')
    else:
        flash('Please enter a valid ticker symbol', 'error')
    return redirect(url_for('index'))

@app.route('/remove/<ticker>', methods=['POST'])
def remove(ticker):
    if remove_stock(ticker):
        flash(f'Successfully removed {ticker} from monitoring list', 'success')
    else:
        flash(f'Failed to remove {ticker}', 'error')
    return redirect(url_for('index'))

@app.route('/check-now', methods=['POST'])
def check_now():
    alerts_sent = check_stocks()
    flash(f'Manual check completed. {alerts_sent} alert(s) sent.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
