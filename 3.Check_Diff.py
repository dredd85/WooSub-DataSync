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

# checking if stocks online aren't bigger then local
df_low_stock = panda_querry("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt on prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan < prod_woo.Stan
AND prod_woo.Status != 'outofstock';
""")
# checking products out of stock in Woo
df_low_stock_woo = panda_querry("""
SELECT prod_woo.Nazwa, prod_woo.Symbol, prod_woo.Stan as Stan_Woo, prod_subiekt.Stan as Stan_Sub 
FROM prod_woo join prod_subiekt on prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Stan > prod_woo.Stan
AND prod_woo.Status = 'outofstock';
""")
# counting rows in out of stock querries
out_of_stock_woo = row_count('SELECT count(Nazwa) FROM prod_woo WHERE Status = \'outofstock\'')
out_of_stock_sub = row_count('SELECT count(Nazwa) FROM prod_subiekt Where prod_subiekt.Stan < prod_subiekt.Stan_Minimalny')

# checking if the out of stock match
if out_of_stock_sub < out_of_stock_woo:
    print('Woo Database out of stock products: {}'.format(out_of_stock_woo))
    print('Subiekt Database out of stock products: {}'.format(out_of_stock_sub))
    print('Check those products: ','\n', df_low_stock_woo)  
    print('\n''Also check NEWLY ADDED products in Woocoommerce')
elif out_of_stock_sub > out_of_stock_woo:
    print('Woo Database out of stock products: {}'.format(out_of_stock_woo))
    print('Subiekt Database out of stock products: {}'.format(out_of_stock_sub))
    print('Check those products: ', '\n', df_low_stock)
    df_low_stock.to_csv('Subiekt_Woocommerce/low_stock_raport.csv', encoding='utf-8', index=False)
else:
    print('\n''Out of stock products MATCH')
# counting all rows in both tables 
row_count_woo = row_count('Select count(Nazwa) From prod_woo')
row_count_sub = row_count('Select count(Nazwa) From prod_subiekt')

df_diff_stock = panda_querry("""
select prod_woo.Symbol, prod_subiekt.Symbol as Symbol_Sub, prod_woo.Nazwa , prod_woo.Stan as Stan_Online, 
prod_subiekt.Stan as Stan_Local from prod_woo
left join prod_subiekt on prod_woo.Symbol = prod_subiekt.Symbol
WHERE prod_subiekt.Symbol is NULL
order by prod_woo.Nazwa
""",)
# checking for differences of overall number of products
if row_count_sub != row_count_woo:
    print('The number of products in Databases does NOT match')
    print('Woo Database products count: {}'.format(row_count_woo))
    print('Subiekt Database products count: {}'.format(row_count_sub))
    print('Check those products:','\n', df_diff_stock)
    df_diff_stock.to_csv('Subiekt_Woocommerce/diff_stock_raport.csv', encoding='utf-8', index=False)
else:
    print('\n''Overall number of products MATCH')

print('\n''All differences CHECKED')

cursor.close()
conn.close()