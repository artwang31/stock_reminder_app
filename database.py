import sqlite3
from datetime import datetime
from typing import List, Tuple

DB_NAME = 'stocks.db'

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            added_date TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            drop_percentage REAL NOT NULL,
            alert_date TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_stock(ticker: str) -> bool:
    """Add a stock to the monitoring list."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO stocks (ticker, added_date) VALUES (?, ?)',
            (ticker.upper(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_stock(ticker: str) -> bool:
    """Remove a stock from the monitoring list."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM stocks WHERE ticker = ?', (ticker.upper(),))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_all_stocks() -> List[Tuple[int, str, str]]:
    """Get all monitored stocks."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, ticker, added_date FROM stocks ORDER BY ticker')
    stocks = cursor.fetchall()
    conn.close()
    return stocks

def log_alert(ticker: str, drop_percentage: float, price: float):
    """Log an alert to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO alerts (ticker, drop_percentage, alert_date, price) VALUES (?, ?, ?, ?)',
        (ticker, drop_percentage, datetime.now().isoformat(), price)
    )
    conn.commit()
    conn.close()

def get_recent_alerts(limit: int = 50) -> List[Tuple]:
    """Get recent alerts."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT ticker, drop_percentage, alert_date, price FROM alerts ORDER BY alert_date DESC LIMIT ?',
        (limit,)
    )
    alerts = cursor.fetchall()
    conn.close()
    return alerts

def was_alert_sent_today(ticker: str) -> bool:
    """Check if an alert was already sent today for this ticker."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    cursor.execute(
        'SELECT COUNT(*) FROM alerts WHERE ticker = ? AND date(alert_date) = ?',
        (ticker, today)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
