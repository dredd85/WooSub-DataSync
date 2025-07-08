from woocommerce import API
import sqlite3
import os
import logging
from datetime import datetime

# ----------------------
# Setup logging
# ----------------------

log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.info("Script started")

# ----------------------
# Load API credentials
# ----------------------

var = 'api_key'
try:
    cred = os.getenv(var)
    if not cred or len((var_unpacked := cred.split(';'))) != 3:
        logging.error(f"Environment variable '{var}' is missing or malformed. Expected format: url;consumer_key;consumer_secret")
        quit()
    url, consumer_key, consumer_secret = var_unpacked
    logging.info("API credentials loaded successfully")
except Exception:
    logging.exception("Failed to load or parse API credentials")
    quit()

# ----------------------
# Initialize WooCommerce API
# ----------------------

wcapi = API(url, consumer_key, consumer_secret, version="wc/v3", timeout=10)

# ----------------------
# Connect to SQLite and prepare table
# ----------------------

try:
    conn = sqlite3.connect('DB_compare.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT Nazwa FROM prod_woo')
        conn.commit()
        cur.execute('DELETE FROM prod_woo')
        logging.info("Table 'prod_woo' found and cleared")
    except:
        cur.execute('CREATE TABLE prod_woo (ID VARCHAR(255), Symbol VARCHAR(255), Nazwa TEXT, Stan INT, Status TEXT)')
        conn.commit()
        logging.info("Table 'prod_woo' created")

    # ----------------------
    # Define product fetch function
    # ----------------------

    def fetch_products(stock_status):
        logging.info(f"Start fetching products with stock_status = '{stock_status}'")
        page = 1
        product_count = 0
        while True:
            try:
                products = wcapi.get('products', params={
                    'per_page': 50,
                    'stock_status': stock_status,
                    'page': page
                }).json()
            except Exception:
                logging.exception(f"API request failed for stock_status = '{stock_status}' on page {page}")
                break

            if not products:
                logging.info(f"No more products with stock_status = '{stock_status}' found (page {page})")
                break

            for item in products:
                product_count += 1
                logging.debug(f"{product_count}. ID: {item['id']}, SKU: {item['sku']}, Name: {item['name']}, Qty: {item.get('stock_quantity')}, Status: {item['stock_status']}")
                cur.execute('''INSERT OR IGNORE INTO prod_woo (ID, Symbol, Nazwa, Stan, Status)
                               VALUES (?, ?, ?, ?, ?)''',
                            (item['id'], item['sku'], item['name'], item.get('stock_quantity'), item['stock_status']))
                conn.commit()

            page += 1

        logging.info(f"Fetched {product_count} products with stock_status = '{stock_status}'")

    # ----------------------
    # Fetch products by stock status
    # ----------------------

    fetch_products('instock')
    fetch_products('outofstock')

    # ----------------------
    # Final summary and cleanup
    # ----------------------

    cur.execute('SELECT COUNT(Nazwa) FROM prod_woo')
    rowcount = cur.fetchone()[0]
    logging.info(f"Inserted {rowcount} total products into 'prod_woo' table")

    cur.close()
    conn.close()

except Exception:
    logging.exception("Critical failure during API sync or database operation")
    quit()
logging.info("Script completed.")