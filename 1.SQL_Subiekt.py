import pyodbc
import sqlite3
import pandas as pd
#database server and login
cnxn_str = ("Driver={SQL Server Native Client 11.0};" #insert database info
            "Server=;"            
            "Database=;"     
            "UID=;"
            "PWD=;")
#connecting database and selecting values
cnxn = pyodbc.connect(cnxn_str)
cursor = cnxn.cursor()
query = "select distinct tw_id, tw_DostSymbol, tw_Nazwa, tw_StanMin, cht_IdCecha from dbo.tw__Towar inner join dbo.tw_Stan on dbo.tw_Stan.st_Towid = dbo.tw__Towar.tw_id inner join dbo.tw_CechaTw on dbo.tw__Towar.tw_id = dbo.tw_CechaTw.cht_IdTowar where tw_StanMin != 0 and cht_IdCecha = 8;"

df = pd.read_sql(query, cnxn)
#making copy of dataframe
df_DB_copy = df.copy()

print('Data base copy : Done')
#connecting to sqlite database
conn = sqlite3.connect('DB_compare.db') 
curr = conn.cursor()
print('Connectioon to SQLITE : Established')
data = df_DB_copy
#buidling a dataframe from copy df_DB
df_sub = pd.DataFrame(data, columns= ['tw_id','tw_DostSymbol','tw_Nazwa'])
df_sub.to_sql('prod_subiekt', conn, if_exists='replace', index = False)

#selecting from table prod_subiekt in DB_compare
curr.execute('''  
		SELECT * FROM prod_subiekt
          ''')

df_sub = pd.DataFrame(curr.fetchall(), columns=['tw_id','tw_DostSymbol','tw_Nazwa'])    
print (df_sub)
cursor.close()
curr.close()




