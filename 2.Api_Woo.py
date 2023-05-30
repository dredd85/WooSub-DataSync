from woocommerce import API
import json
import sqlite3

wcapi = API(
    url=input('Insert Woocommerce site:'),
    consumer_key=input('Insert consumer key:'),
    consumer_secret=input('Insert secret key:'),
    version="wc/v3",
    timeout=10
)
conn = sqlite3.connect('DB_compare.db')
cur = conn.cursor()

# Clearing table or creating
try:
    cur.execute('SELECT Nazwa FROM prod_woo')
    conn.commit()
except:
    cur.execute('CREATE TABLE prod_woo (Symbol VARCHAR(255), Nazwa TEXT, Stan INT, Status TEXT)')
    conn.commit()
else:
    cur.execute('DELETE FROM prod_woo')

# Defining fetch function
def fetch_products(stock):
    page = 1
    product_count = 0
    while True:
        products = wcapi.get('products', params={'per_page': 50, 'stock_status': {stock}, 'page': page}).json()
        
        if len(products) == 0: # no more products
            print('Products {} fetched from API'.format(stock))
            break   
        for item in products:
            product_count += 1
            print(product_count)
            print('ID:', item['id'])
            print('Nazwa:', item['name'])
            print('Kod:', item['sku'])
            print('Stan:', item['stock_status'])
            cur.execute('''INSERT OR IGNORE INTO prod_woo (Symbol, Nazwa, Stan, Status)
                        VALUES (?, ?, ?, ?)''', (item['sku'], item['name'], item['stock_quantity'], item['stock_status']))
            conn.commit()
            
        page = page + 1
        print(page)
    print('Fetched:',product_count, 'products')

# Fetching in stock products
fetch_products('instock')

# Fetching out of stock products
fetch_products('outofstock')

cur.execute('SELECT COUNT(Nazwa) FROM prod_woo')
rowcount = cur.fetchone()[0]
print('Inserted {} products into the database'.format(rowcount))

cur.close()
conn.close()
