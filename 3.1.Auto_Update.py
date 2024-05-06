import sqlite3
import pandas as pd

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
WHERE Stan > 0""")

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
        
