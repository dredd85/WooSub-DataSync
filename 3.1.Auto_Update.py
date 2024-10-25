import sqlite3
import pandas as pd
from woocommerce import API
import os

print('This script is built for auto update stocks in WooCommerce')
print('*******')
print('Part I: Updates products that should be in out_of_stock status in Woo')
print('Part II: Updates prododucts that should be instock in Woo')
print('*******')
print('Before both user decision and credentials are needed')
print('')
print('Proceed with Part I?')
user_decision = input('Proceed? Y/N: ').strip().lower()
if user_decision != 'y':
    print('To try again reload the script')
    quit()
# Connect to SQLite database
conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# Define simple queries
def panda_query(query):
    return pd.read_sql(query, conn)

# Fetch products from local and online databases
out_of_stock_local = panda_query("""
    SELECT Symbol FROM prod_subiekt
    WHERE Stan_Minimalny > Stan
""")

woo_products = panda_query("""
    SELECT ID, Symbol FROM prod_woo
    WHERE Stan > 0 OR Status = 'instock'
""")

# Convert 'Symbol' columns to string type in both DataFrames
out_of_stock_local['Symbol'] = out_of_stock_local['Symbol'].astype(str)
woo_products['Symbol'] = woo_products['Symbol'].astype(str)

products_to_update = []

# Iterate through products from the website
for index, product in woo_products.iterrows():
    sku = product['Symbol']
    # Check if SKU exists in the products with local stock lower than minimal
    if sku in out_of_stock_local['Symbol'].values:
        products_to_update.append((product['ID'], sku))

print('Auth from env (E) or input (I)?')
print('For env (E) auth ensure correct variable name')
answer = input('Type E or I: ')
answer = answer.upper()
possible_answers = ['E', 'I']

if answer not in possible_answers:
    print('Wrong input, try again')
    quit()

if answer == possible_answers[0]:
    var = input('Type variable name: ')
    try:
        cred = os.getenv(var)
        var_unpacked = cred.split(';')
        url = var_unpacked[0]
        consumer_key = var_unpacked[1]
        consumer_secret = var_unpacked[2]
        print('File load success')  
    except FileNotFoundError as E:
        print('***Auth failed*** Error')
        print(E)
        quit()
else:
    url = input('Insert Woocommerce site: ')
    consumer_key = input('Insert consumer key: ')
    consumer_secret = input('Insert secret key: ')

# Initialize WooCommerce API
wcapi = API(url, consumer_key, consumer_secret, version="wc/v3", timeout=10)

if not products_to_update:
    print('No products to update')
else:
    print(f'Products to update: {products_to_update}')
    user_decision = input('Proceed? Y/N: ').strip().lower()
    if user_decision == "y":
        print('Update in progress...')
        # Check products in WooCommerce store
        for product_id, sku in products_to_update:
            print(f"Product to update: ID={product_id}, SKU={sku}")
            # Uncomment the following block to enable updating
            try:
                product_data = {'stock_quantity': 0}  # Set the new stock level to 0
                response = wcapi.put(f"products/{product_id}", data=product_data).json()
                if 'message' in response:
                    print(f"Error updating stock level for product with SKU {sku}: {response['message']}")
                else:
                    print(f"Stock level updated successfully for product with SKU {sku}")
            except Exception as e:
                print(f"Error updating stock level for product with SKU {sku}: {e}")
    else:
        print('Update cancelled.')

# Second update section for product that should be instock in Woo

print('Proceed with Part II?')
user_decision = input('Proceed? Y/N: ').strip().lower()
if user_decision != 'y':
    print('To try again reload the script')
    quit()

# Fetch products from local and online databases
instock_local = panda_query("""
    SELECT Symbol, Stan FROM prod_subiekt
    WHERE Stan_Minimalny <= Stan
""")

out_of_stock_woo = panda_query("""
    SELECT ID, Symbol FROM prod_woo
    WHERE Stan = 0 OR Status = 'outofstock'
""")

products_to_update = []

# Iterate through products from the website
for index, product in instock_local.iterrows():
    sku = product['Symbol']
    stock_level = product['Stan']  # Extract the stock level from instock_local
    # new stock level
    new_stock_level = round(stock_level / 2)

    # Check if SKU exists in the out_of_stock_woo DataFrame
    match = out_of_stock_woo[out_of_stock_woo['Symbol'] == sku]

    if not match.empty:
        product_id = match.iloc[0]['ID']  # Get the corresponding ID from out_of_stock_woo
        
        # Append product_id, sku, and new_stock_level to products_to_update list
        products_to_update.append((product_id, sku, new_stock_level))

# Updating Part II

if not products_to_update:
    print('No products to update')
    exit()
else:
    print(f'Products to update: {products_to_update}')
    user_decision = input('Proceed? Y/N: ').strip().lower()
    if user_decision == "y":
        print('Update in progress...')
        # Check products in WooCommerce store
        for product_id, sku, new_stock_level in products_to_update:
            print(f"Product to update: ID={product_id}, SKU={sku}")
            # Uncomment the following block to enable updating
            try:
                product_data = {'stock_quantity': new_stock_level}  # Set the new stock level to 0
                response = wcapi.put(f"products/{product_id}", data=product_data).json()
                if 'message' in response:
                    print(f"Error updating stock level for product with SKU {sku}: {response['message']}")
                else:
                    print(f"Stock level updated successfully for product with SKU {sku}")
            except Exception as e:
                print(f"Error updating stock level for product with SKU {sku}: {e}")
    else:
        print('Update cancelled.')
