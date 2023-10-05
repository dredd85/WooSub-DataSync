from woocommerce import API
import sqlite3

print('Auth from file (F) or input (I)?')
print('For file (F) auth ensure to load file from working directory')
answer = input('Type F or I: ')
answer = answer.upper()
possible_answers = ['F', 'I']

if answer not in possible_answers:
    print('Wrong input, try again')
    quit()

if answer == possible_answers[0]:
    key_list = []
    file = input('Type the file name: ')
    try:
        API_key = open(file, "r")
        for line in API_key:
            line = line.strip()
            key_list.append(line)
        url = key_list[0]
        consumer_key = key_list[1]
        consumer_secret = key_list[2]
        print('File load success')   
    except FileNotFoundError as E:
        print('***Auth failed*** Error')
        print(E)
        quit()
else:
    url = input('Insert Woocommerce site: ')
    consumer_key = input('Insert consumer key: ')
    consumer_secret = input('Insert secret key: ')

wcapi = API(url, consumer_key, consumer_secret, version="wc/v3", timeout=10)

try:
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
except:
    print('Connection failed, check the API authentication and try again')