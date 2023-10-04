import pyodbc
import sqlite3
import pandas as pd

print('Auth from file (F) or input (I)?')
print('For file (F) auth ensure to load file from working directory')
answer = input('Type F or I: ')
answer = answer.upper()
possible_answers = ['F', 'I']

if answer not in possible_answers:
    print('Wrong input, try again')
    quit()

if answer == possible_answers[0]:
    key_list = []
    file = input('Type the file name: ')
    try:
        SQL_key = open(file, "r")
        for line in SQL_key:
            line = line.strip()
            key_list.append(line)
        server = key_list[0]
        database = key_list[1]
        username = key_list[2]
        password = key_list[3]
        print('File load success')   
    except FileNotFoundError as E:
        print('***Auth failed*** Error')
        print(E)
        quit()
else:
    server = input("Insert server name: ")
    database = input("Insert database name: ")
    username = input("Insert login: ")
    password = input("Insert password: ")

# Connect to SQL Server database and execute a query

query = "SELECT dbo.tw__Towar.tw_Nazwa as Nazwa, dbo.tw__Towar.tw_DostSymbol as Symbol, sum(dbo.tw__Towar.tw_StanMin)/2 as Stan_Minimalny, sum(dbo.tw_Stan.st_Stan) as Stan FROM dbo.tw__Towar JOIN dbo.tw_Stan on dbo.tw_Stan.st_Towid = dbo.tw__Towar.tw_id JOIN dbo.tw_CechaTw on dbo.tw__Towar.tw_id = dbo.tw_CechaTw.cht_IdTowar WHERE tw_StanMin != 0 and cht_IdCecha = 8 GROUP by dbo.tw__Towar.tw_Nazwa, dbo.tw__Towar.tw_DostSymbol;"
cnxn_str = f"DRIVER=SQL Server Native Client 11.0;SERVER={server};DATABASE={database};UID={username};PWD={password}"

try:
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

except:
    print('Connection failed, please check server authentication and try again')



