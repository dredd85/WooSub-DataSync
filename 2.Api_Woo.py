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

# Deleting existing rows
cur.execute('DELETE FROM prod_woo')
conn.commit()

page = 1
product_count = 0

# Fetching in stock products
while True:
    products = wcapi.get('products', params={'per_page': 50, 'stock_status': 'instock', 'page': page}).json()
    
    if len(products) == 0: # no more products
        print('Products in stock fetched')
        break   
    for item in products:
        product_count += 1
        print(product_count)
        print('ID:', item['id'])
        print('Nazwa:', item['name'])
        print('Kod:', item['sku'])
        print('Stan:', item['stock_status'])
        cur.execute('''INSERT OR IGNORE INTO prod_woo (id, kod_Dost, nazwa)
                    VALUES (?, ?, ?)''', (item['id'], item['sku'], item['name']))
        conn.commit()
        
    page = page + 1
    print(page)

page = 1

# Fetching out of stock products
while True:
    products = wcapi.get('products', params={'per_page': 50, 'stock_status': 'outofstock', 'page': page}).json()
    
    if len(products) == 0: # no more products
        print('Products out of stock fetched')
        break   
    for item in products:
        product_count += 1
        print(product_count)
        print('ID:', item['id'])
        print('Nazwa:', item['name'])
        print('Kod:', item['sku'])
        print('Stan:', item['stock_status'])
        cur.execute('''INSERT OR IGNORE INTO prod_woo (id, kod_Dost, nazwa)
                    VALUES (?, ?, ?)''', (item['id'], item['sku'], item['name']))
        conn.commit()
        
    page = page + 1
    print(page)

cur.close()
