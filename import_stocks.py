import csv
from database import init_db, add_stock

def import_stocks_from_csv(csv_file):
    """Import stocks from CSV file."""
    init_db()

    added = []
    skipped = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row['Ticker'].strip()

            # Skip deposit sweep accounts
            if 'DEPOSIT' in row['Description'].upper():
                print(f"Skipping: {ticker} (deposit account)")
                skipped.append(ticker)
                continue

            if add_stock(ticker):
                print(f"✓ Added: {ticker}")
                added.append(ticker)
            else:
                print(f"- Already exists: {ticker}")
                skipped.append(ticker)

    print(f"\n{'='*50}")
    print(f"Import complete!")
    print(f"Added: {len(added)} stocks")
    print(f"Skipped: {len(skipped)} stocks")
    print(f"{'='*50}")

    return added, skipped

if __name__ == '__main__':
    import_stocks_from_csv('positions.csv')
