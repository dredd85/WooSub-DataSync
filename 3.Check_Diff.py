import pyodbc
import sqlite3
import pandas as pd

conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# definig fucntion for counting rows
def row_count(querry):
    cursor.execute('{}'.format(querry))
    count_val = cursor.fetchone()[0]
    conn.commit()
    return count_val

# defining simple querries
def panda_querry(querry):
    sql = pd.read_sql('{}'.format(querry),conn)
    return sql

# out of stock products count in both databases
out_of_stock_woo = row_count('SELECT count(Nazwa) FROM prod_woo WHERE Status = \'outofstock\'')
out_of_stock_sub = row_count('SELECT count(Nazwa) FROM prod_subiekt Where prod_subiekt.Stan < prod_subiekt.Stan_Minimalny')

# products with low stock locally -> should be out of stock online
df_low_stock = panda_querry("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan < prod_woo.Stan
AND prod_woo.Status != 'outofstock';
""")
# products with high stock locally -> should be in stock online
df_low_stock_woo = panda_querry("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan > prod_woo.Stan
AND prod_woo.Status = 'outofstock';
""")

# checking if the out of stock match
if df_low_stock_woo.empty:
    print('Subiekt low stock products CHECKED')
else:
    print('Woo Database out of stock products: {}'.format(out_of_stock_woo))
    print('Subiekt Database out of stock products: {}'.format(out_of_stock_sub))
    print('Check those products: ','\n', df_low_stock_woo)

if df_low_stock.empty:
    print('\n''Woo low stock products CHECKED')
else:
    print('Woo Database out of stock products: {}'.format(out_of_stock_woo))
    print('Subiekt Database out of stock products: {}'.format(out_of_stock_sub))
    print('Check those products: ', '\n', df_low_stock)

# counting all rows in both tables 
row_count_woo = row_count('SELECT COUNT(Nazwa) FROM prod_woo')
row_count_sub = row_count('SELECT COUNT(Nazwa) FROM prod_subiekt')

# looking for products with no match in the Woo database
df_diff_stock = panda_querry("""
SELECT prod_woo.Symbol, prod_subiekt.Symbol as Symbol_Sub, prod_woo.Nazwa , prod_woo.Stan as Stan_Online, 
prod_subiekt.Stan as Stan_Local FROM prod_woo
LEFT JOIN prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Symbol is NULL
ORDER BY prod_woo.Nazwa
""",)
# checking for differences of overall number of products
if row_count_sub != row_count_woo:
    print('The number of products in Databases does NOT match')
    print('Woo Database products count: {}'.format(row_count_woo))
    print('Subiekt Database products count: {}'.format(row_count_sub))
    print('Check those products:','\n', df_diff_stock)
    print('Also check new added products in Woo Store')
else:
    print('\n''Overall number of products MATCH')

print('\n''Quantity differences CHECKED')

cursor.close()
conn.close()