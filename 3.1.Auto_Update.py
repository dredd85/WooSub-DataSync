import sqlite3
import pandas as pd
from woocommerce import API

conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# defining simple querries
def panda_querry(querry):
    sql = pd.read_sql('{}'.format(querry),conn)
    return sql

out_of_stock_local = panda_querry("""
SELECT Symbol FROM prod_subiekt
WHERE Stan_Minimalny > Stan""")

woo_products = panda_querry("""
SELECT Symbol FROM prod_woo
WHERE Stan > 0
OR Status = "instock"
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
        products_to_update.append(sku)
    
if not products_to_update:
    print('No products to update')
    exit()
else:
    print(f'Products to update: {products_to_update}')
    user_decision = input('Proceed? Y/N: ').strip().lower()
    if user_decision == "y":
        print('Update in progress...')
    else:
        quit()
    
# WooCommerce API credentials
url = 'https://armatura-sanitarna.com/'
consumer_key = 'ck_0a4dc31230734eb0227ca96c8eb224a1d4614edf'
consumer_secret = 'cs_b3cb8c361d8a075d6437055400adedc4cbc2e0f1'

wcapi = API(url, consumer_key, consumer_secret, version="wc/v3", timeout=10)

def get_product_id_by_sku(wcapi, sku):
    try:
        response = wcapi.get('products', params={'sku': sku}).json()
        if response:
            product_id = response[0]['id']
            product_name = response[0]['name']
            print(f"Found product: ID={product_id}, Name={product_name}, SKU={sku}")
            return product_id, product_name  # Return both ID and Name
        else:
            print(f"No product found with SKU {sku}")
            return None
    except Exception as e:
        print(f"Error fetching product ID for SKU {sku}: {e}")
        return None

# Fetch product ID based on SKU
product_id = get_product_id_by_sku(wcapi, sku)

print(product_id)
'''
if product_id is not None:
    # Update product stock level using the fetched product ID
    try:
        product_data = {'stock_quantity': new_stock_level}
        response = wcapi.put(f"products/{product_id}", data=product_data).json()
        if 'message' in response:
            print(f"Error updating stock level for product with SKU {sku}: {response['message']}")
        else:
            print(f"Stock level updated successfully for product with SKU {sku}")
    except Exception as e:
        print(f"Error updating stock level for product with SKU {sku}: {e}")
else:
    print("No product ID found for the given SKU, unable to update stock level.")
'''