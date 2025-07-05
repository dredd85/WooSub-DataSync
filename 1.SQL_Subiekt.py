import sqlalchemy as sa
import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime

# Ensure logs folder exists
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Full log path
log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()  # Prints to console
    ]
)

logging.info("Script Starts")

# Get credentials
var = 'sql_key'
try:
    logging.info("Fetching credentials")
    cred = os.getenv(var)
    if not cred:
        raise ValueError(f"No credentials found in environment variable: {var}")
    var_unpacked = cred.split(';')
    server = var_unpacked[0]
    database = var_unpacked[1]
    username = var_unpacked[2]
    password = var_unpacked[3]
    logging.info("Database credentials loaded successfully.")
except Exception as e:
    logging.error("***Auth failed***", exc_info=True)
    quit()
    logging.info("Script failed due to error")
logging.info("Credentials Fetched")

# Build SQLAlchemy connection string for SQL Server
cnxn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

# SQL Query
query = """
    SELECT 
        dbo.tw__Towar.tw_Nazwa as Nazwa,
        dbo.tw__Towar.tw_DostSymbol as Symbol,
        dbo.tw__Towar.tw_StanMin as Stan_Minimalny,
        dbo.tw_Stan.st_Stan as Stan 
    FROM dbo.tw__Towar 
    JOIN dbo.tw_Stan on dbo.tw_Stan.st_Towid = dbo.tw__Towar.tw_id 
    JOIN dbo.tw_CechaTw on dbo.tw__Towar.tw_id = dbo.tw_CechaTw.cht_IdTowar 
    WHERE tw_StanMin != 0 and cht_IdCecha = 8 and st_MagId = 4;
"""

try:
    logging.info("Connecting to SQL Server...")
    engine = sa.create_engine(cnxn_str)
    with engine.connect() as cnxn:
        df_sqlserver = pd.read_sql(query, cnxn)
    logging.info("Data fetched successfully from SQL Server.")

    conn = sqlite3.connect("DB_compare.db")
    df_sqlserver.to_sql("prod_subiekt", conn, if_exists="replace", index=False)
    logging.info("Data saved to SQLite database.")

    df_sqlite = pd.read_sql("SELECT * FROM prod_subiekt", conn)
    logging.info("Data retrieved from SQLite:")
    logging.info(f"\n{df_sqlite}")

    conn.close()
    logging.info("Connections closed. Script completed successfully.")

except Exception as e:
    logging.error("Connection or execution failed.", exc_info=True)


logging.info("Script succesful")