import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

def panda_querry(querry):
    sql = pd.read_sql('{}'.format(querry),conn)
    return sql

def row_count(querry):
    cursor.execute('{}'.format(querry))
    count_val = cursor.fetchone()[0]
    conn.commit()
    return count_val

# Products without proper codes in subiekt database 
not_matching_prod = panda_querry("""
SELECT prod_woo.Symbol, prod_subiekt.Symbol AS Symbol_Sub, prod_woo.Nazwa FROM prod_woo
LEFT JOIN prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Symbol IS NULL
ORDER BY prod_woo.Nazwa
""")

database_count = row_count("""
SELECT  count(prod_woo.Nazwa) FROM prod_woo
LEFT JOIN prod_subiekt ON prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Symbol IS NULL
ORDER BY prod_woo.Nazwa
""")

if not_matching_prod.empty:
    print('Symbols in the databases MATCH')
else:
    print('{} products with symbols not matching'.format(database_count))
    print('Check those products:''\n', not_matching_prod,'\n')

# comparing out of stock products by symbols
subiekt_woo_compare = panda_querry("""
SELECT prod_subiekt.Symbol FROM prod_subiekt
WHERE prod_subiekt.Stan < prod_subiekt.Stan_Minimalny
EXCEPT
SELECT prod_woo.Symbol FROM prod_woo
WHERE prod_woo.Status = 'outofstock';
""")

if subiekt_woo_compare.empty:
    print('Low stock in Subiekt CHECKED''\n')
else:
    print('Products that should be changed to out of stock in Woo:''\n',subiekt_woo_compare)

woo_subiekt_compare = panda_querry("""
SELECT prod_woo.Symbol FROM prod_woo
WHERE prod_woo.Status = 'outofstock'
EXCEPT
SELECT prod_subiekt.Symbol FROM prod_subiekt
WHERE prod_subiekt.Stan < prod_subiekt.Stan_Minimalny;
""")

if woo_subiekt_compare.empty:
    print('Low stock in Woo CHECKED','\n')
else:
    print('Products IN out of stock in Woo which could be in stock''\n',woo_subiekt_compare)

# Products worth checking local stock < online stock
stock_check = panda_querry("""
SELECT prod_woo.Symbol, prod_subiekt.Symbol AS Symbol_Sub, prod_woo.Nazwa, prod_woo.Stan AS Stan_Online, 
prod_subiekt.Stan AS Stan_Local FROM prod_woo
JOIN prod_subiekt on prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_woo.Stan > prod_subiekt.stan 
ORDER BY prod_woo.Nazwa
""")

if stock_check.empty:
    print('Woocommerce products stock CHECKED')
    print('All products symbols CHECKED')
else:
    print('Products worth checking: Higher Woo stock than Local')
    print(stock_check)

cursor.close()
conn.close()