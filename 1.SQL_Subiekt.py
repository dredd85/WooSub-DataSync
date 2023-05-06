import pyodbc
import sqlite3
import pandas as pd

# Connect to SQL Server database and execute a query
server = input("Insert server name:")
database = input("Insert database name:")
username = input("Insert login:")
password = input("Insert password:")
query = "select distinct tw_id, tw_DostSymbol, tw_Nazwa, tw_StanMin, cht_IdCecha from dbo.tw__Towar inner join dbo.tw_Stan on dbo.tw_Stan.st_Towid = dbo.tw__Towar.tw_id inner join dbo.tw_CechaTw on dbo.tw__Towar.tw_id = dbo.tw_CechaTw.cht_IdTowar where tw_StanMin != 0 and cht_IdCecha = 8;"
cnxn_str = f"DRIVER=SQL Server Native Client 11.0;SERVER={server};DATABASE={database};UID={username};PWD={password}"
cnxn = pyodbc.connect(cnxn_str)
df_sqlserver = pd.read_sql(query, cnxn)

# Save the data to a SQLite database
conn = sqlite3.connect("DB_compare.db")
df_sqlserver.to_sql("prod_subiekt", conn, if_exists="replace", index=False)

# Retrieve the data from the SQLite database
df_sqlite = pd.read_sql("SELECT * FROM prod_subiekt", conn)

# Print the retrieved data
print(df_sqlite)

# Close the connections
cnxn.close()
conn.close()




