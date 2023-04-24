from woocommerce import API
import json
import sqlite3

wcapi = API(
    url="https://armatura-sanitarna.com/",
    consumer_key= input('Insert consumer key:'),
    consumer_secret= input('Insert secret key:'),
    version="wc/v3",
    timeout = 10
)
page = 1
prod_count = 1

conn = sqlite3.connect('DB_compare.db')
cur = conn.cursor()

while True:
    products = wcapi.get('products', params={'per_page': 50, 'stock_status': 'instock', 'page': page}).json()
    
    if len(products) == 0: # no more products
        print('All products fetched')
        break   
    for item in products:
        prod_count += 1
        print(prod_count)
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
