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
print("Summary of products for ecom:")
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


