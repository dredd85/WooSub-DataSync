import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# Define simple queries
def panda_query(query):
    return pd.read_sql(query, conn)

# Fetch products from local and online databases
out_of_stock_sub = panda_query("""
    SELECT Symbol FROM prod_subiekt
    WHERE Stan_Minimalny > Stan
""")

in_stock_woo = panda_query("""
    SELECT ID, Symbol FROM prod_woo
    WHERE Stan > 0 OR Status = 'instock'
""")

# fetch products that are in both databases

overall_woo = panda_query("""SELECT Symbol, Nazwa FROM prod_woo""")
overall_sub = panda_query("""SELECT Symbol, Nazwa FROM prod_subiekt""")


