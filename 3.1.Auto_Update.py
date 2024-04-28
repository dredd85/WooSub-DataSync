import sqlite3
import pandas as pd

conn = sqlite3.connect("DB_compare.db")
cursor = conn.cursor()

# defining simple querries
def panda_querry(querry):
    sql = pd.read_sql('{}'.format(querry),conn)
    return sql

out_of_stock_local = panda_querry("""
SELECT * FROM prod_subiekt
WHERE Stan_Minimalny > Stan""")

print(out_of_stock_local)