import sqlalchemy as sa
import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime

# ----------------------
# Setup logging
# ----------------------

# Create a 'logs' folder if it doesn't exist
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Define log file with timestamp
log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logging.info("Script started.")

# ----------------------
# Fetch credentials from environment variable
# ----------------------

var = 'sql_key'
try:
    logging.info("Fetching credentials from environment variable...")
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
    logging.exception("Authentication failed.")
    logging.info("Script terminated due to credential error.")
    quit()

# ----------------------
# Build SQL connection and query
# ----------------------

# SQLAlchemy connection string for SQL Server
cnxn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

# Query to extract stock and product data from Subiekt
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

# ----------------------
# Execute data operations
# ----------------------

try:
    logging.info("Connecting to SQL Server...")
    engine = sa.create_engine(cnxn_str)

    with engine.connect() as cnxn:
        df_sqlserver = pd.read_sql(query, cnxn)
    logging.info(f"Fetched {len(df_sqlserver)} records from SQL Server.")

    # Save data to local SQLite database
    conn = sqlite3.connect("DB_compare.db")
    df_sqlserver.to_sql("prod_subiekt", conn, if_exists="replace", index=False)
    logging.info("Data written to SQLite database: 'prod_subiekt' table.")

    # Retrieve and preview data from SQLite
    df_sqlite = pd.read_sql("SELECT * FROM prod_subiekt", conn)
    logging.info("Sample of retrieved data from SQLite:")
    logging.info(f"\n{df_sqlite.head()}")

    conn.close()
    logging.info("Database connections closed. Data sync completed.")

except Exception:
    logging.exception("Database connection or data processing failed.")
    quit()
logging.info("Script completed.")