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
    print('There are {} with symbols not matching between databases'.format(database_count))
    print('Check those products:''\n', not_matching_prod,'\n')

# Raport to compare the codes from both databases that are out of stock

out_of_stock_compare = panda_querry("""
SELECT prod_subiekt.Symbol FROM prod_subiekt
WHERE prod_subiekt.Stan < prod_subiekt.Stan_Minimalny
EXCEPT
SELECT prod_woo.Symbol FROM prod_woo
WHERE prod_woo.Status = 'outofstock';
""")

if out_of_stock_compare.empty:
    print('Out of stock FIRST check PASSED')
else:
    print('Products NOT in out of stock Woo with low stock locally''\n',out_of_stock_compare)

out_of_stock_compare = panda_querry("""
SELECT prod_woo.Symbol FROM prod_woo
WHERE prod_woo.Status = 'outofstock'
EXCEPT
SELECT prod_subiekt.Symbol FROM prod_subiekt
WHERE prod_subiekt.Stan < prod_subiekt.Stan_Minimalny;
""")

if out_of_stock_compare.empty:
    print('Out of stock SECOND check PASSED')
else:
    print('Products IN out of stock in Woo which could be in stock''\n',out_of_stock_compare)

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