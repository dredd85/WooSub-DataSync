import pyodbc
import sqlite3
import pandas as pd

conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# Reading products which stock < minimal stock in local database
df_sqlite = pd.read_sql("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt on prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan < prod_woo.Stan
AND prod_woo.Status != 'outofstock';
""", conn)

# Counting out of stock products
cursor.execute("""
SELECT count(prod_subiekt.Nazwa) AS Nazwa, prod_subiekt.Symbol AS Symbol, prod_subiekt.Stan AS Stan 
FROM prod_subiekt
WHERE prod_subiekt.Stan < prod_subiekt.Stan_Minimalny;
""")
rowcount = cursor.fetchone()[0]

if df_sqlite.empty:
    print('The number of out of stock products in databases is {}'.format(rowcount))
    print('Checked all the stock differences')
else:
    print('Check those products for stock differences: ')
    print(df_sqlite)

cursor.close()
conn.close()