import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# Define simple queries
def panda_query(query):
    return pd.read_sql(query, conn)

# Fetch products from local and online databases
overall_woo = panda_query("""SELECT Symbol, Nazwa FROM prod_woo""")
overall_sub = panda_query("""SELECT Symbol, Nazwa FROM prod_subiekt""")

# Calculate total counts
total_woo = len(overall_woo)
total_sub = len(overall_sub)

# Initialize lists to store differences
woo_not_in_sub = []
sub_not_in_woo = []

# Convert 'Symbol' to a set for faster lookup
sub_symbols = set(overall_sub['Symbol'])

# Check for products in woo but not in sub
for index, product in overall_woo.iterrows():
    if product['Symbol'] not in sub_symbols:
        woo_not_in_sub.append(product)

# Convert 'Symbol' to a set for faster lookup
woo_symbols = set(overall_woo['Symbol'])

# Check for products in sub but not in woo
for index, product in overall_sub.iterrows():
    if product['Symbol'] not in woo_symbols:
        sub_not_in_woo.append(product)

# Calculate counts of products not in the other dataset
count_woo_not_in_sub = len(woo_not_in_sub)
count_sub_not_in_woo = len(sub_not_in_woo)

# Print overall counts and differences
print("Report: Products for Ecommerce Summary:")
print(f"Total products in WOO: {total_woo}")
print(f"Total products in SUB: {total_sub}")
print("")

print(f"Products in WOO but not in SUB: {count_woo_not_in_sub}")
for product in woo_not_in_sub:
    print(f"Symbol: {product['Symbol']} - Nazwa: {product['Nazwa']}")

print("")
print(f"Products in SUB but not in WOO: {count_sub_not_in_woo}")
for product in sub_not_in_woo:
    print(f"Symbol: {product['Symbol']} - Nazwa: {product['Nazwa']}")

print("")
print('Proceed with Report: Out Of Stock Summary?')
user_decision = input('Proceed? Y/N: ').strip().lower()
if user_decision != 'y':
    print('To view remaining reports reload script')
    quit()

print("")
print('Report: Out Of Stock Summary')
print("")

# Fetch out of stock products from local and online databases
out_of_stock_local = panda_query("""
    SELECT Symbol, Nazwa FROM prod_subiekt
    WHERE Stan_Minimalny > Stan
""")

out_of_stock_woo = panda_query("""
    SELECT Symbol, Nazwa FROM prod_woo
    WHERE Stan <= 0 OR Status = 'outofstock'
""")

# Calculate total counts
total_out_of_stock_local = len(out_of_stock_local)
total_out_of_stock_woo = len(out_of_stock_woo)
print(f"Total products out of stock in WOO: {total_out_of_stock_woo}")
print(f"Total products out of stock in SUB: {total_out_of_stock_local}")

# Initialize lists to store out-of-stock differences
out_of_stock_local_not_in_woo = []
out_of_stock_woo_not_in_local = []

# Convert 'Symbol' to a set for faster lookup
woo_symbols = set(out_of_stock_woo['Symbol'])

# Check for out of stock products in local but not in woo
for index, product in out_of_stock_local.iterrows():
    if product['Symbol'] not in woo_symbols:
        out_of_stock_local_not_in_woo.append(product)

# Convert 'Symbol' to a set for faster lookup
local_symbols = set(out_of_stock_local['Symbol'])

# Check for in stock products in woo but not in local out of stock
for index, product in out_of_stock_woo.iterrows():
    if product['Symbol'] not in local_symbols:
        out_of_stock_woo_not_in_local.append(product)

# Calculate counts of out-of-stock products not in the other dataset
count_out_of_stock_local_not_in_woo = len(out_of_stock_local_not_in_woo)
count_out_of_stock_woo_not_in_local = len(out_of_stock_woo_not_in_local)

# Print out-of-stock differences
if count_out_of_stock_local_not_in_woo > 0:
    print(f"Out of stock in SUB & In Stock in WOO: {count_out_of_stock_local_not_in_woo}")
    for product in out_of_stock_local_not_in_woo:
        print(f"Symbol: {product['Symbol']} - Nazwa: {product['Nazwa']}")
    print('')
    print('Run the Auto_Update script to level the stocks')
else:
    print('')
    print('*No products to set out_of_stock in WOO')
print("")

if count_out_of_stock_woo_not_in_local > 0:
    print(f"Out of stock in WOO & In Stock in SUB: {count_out_of_stock_woo_not_in_local}")
    for product in out_of_stock_woo_not_in_local:
        print(f"Symbol: {product['Symbol']} - Nazwa: {product['Nazwa']}")
    print('')
    print('*Manually update the stocks in WOO to level stocks')
else:
    print('No products to update in SUB')

print("")
print('Proceed with Report: Stock Comparison Summary?')
user_decision = input('Proceed? Y/N: ').strip().lower()
if user_decision != 'y':
    print('To view remaining reports reload script')
    quit()

print("")
print('Report: Stock Comparison Summary')
print("")

# products with low stock locally -> should be out of stock online
sub_low_stock = panda_query("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan < prod_woo.Stan
AND prod_woo.Status != 'outofstock';
""")
# products with high stock locally -> should be in stock online
woo_low_stock = panda_query("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan > prod_woo.Stan
AND prod_woo.Status = 'outofstock';
""")

print('Products with Low Local Stock in Sub:')
print(sub_low_stock)
print('')
print('Products with Higher Stock Locally:')
print(woo_low_stock)