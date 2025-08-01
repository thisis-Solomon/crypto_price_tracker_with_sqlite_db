
import sqlite3
import requests
from datetime import datetime

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1,
    "sparkline": False
}

DB_NAME = "crypto.db"

def fetch_crypto_data():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            coin TEXT,
            price REAL
        )
''')
    
    conn.commit()
    conn.close()
    
def save_to_db(crypto_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for coin in crypto_data:
        cursor.execute('''
            INSERT INTO crypto_prices (timestamp, coin, price)
            VALUES (?, ?, ?)
        ''', (timestamp, coin['id'], coin['current_price']))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(crypto_data)} records to the database.")
    
def search_coin(coin_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, price FROM crypto_prices
        WHERE coin = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (coin_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"timestamp": result[0], "price": result[1]}
    else:
        return None
    
def main():
    create_table()
    print("1. Fetch and store crypto data")
    print("2. Search for a coin by coin name")
    
    choice = input("Enter your choice: ")
    
    if choice == '1':
        crypto_data = fetch_crypto_data()
        if crypto_data:
            save_to_db(crypto_data)
        else:
            print("No data fetched.")
    elif choice == '2':
        coin_name = input("Enter the coin name (e.g., bitcoin): ")
        result = search_coin(coin_name)
        if result:
            print(f"Latest price for {coin_name} is ${result['price']} at {result['timestamp']}.")
        else:
            print(f"No records found for {coin_name}.")
    else:
        print("Invalid choice.")
        
if __name__ == "__main__":
    main()