import logging
import os
import sqlite3
import sqlalchemy as sa
import pandas as pd
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_SQLITE = "DB_compare.db"
DEFAULT_TABLE = "prod_subiekt"

QUERY = """
    SELECT 
        dbo.tw__Towar.tw_Nazwa as name,
        dbo.tw__Towar.tw_DostSymbol as sku,
        dbo.tw__Towar.tw_StanMin as min_stock,
        dbo.tw_Stan.st_Stan as stock_quantity 
    FROM dbo.tw__Towar 
    JOIN dbo.tw_Stan on dbo.tw_Stan.st_Towid = dbo.tw__Towar.tw_id 
    JOIN dbo.tw_CechaTw on dbo.tw__Towar.tw_id = dbo.tw_CechaTw.cht_IdTowar 
    WHERE tw_StanMin != 0 and cht_IdCecha = 8 and st_MagId = 4;
"""


def parse_env_credentials(var_name: str) -> dict:
    cred = os.getenv(var_name)
    if not cred:
        raise ValueError(f"Environment variable '{var_name}' is not set")
    parts = cred.split(";")
    if len(parts) < 4:
        raise ValueError(f"Environment variable '{var_name}' is malformed")
    return {"server": parts[0], "database": parts[1], "username": parts[2], "password": parts[3]}


def prompt_credentials() -> dict:
    server = input("Insert server name: ").strip()
    database = input("Insert database name: ").strip()
    username = input("Insert login: ").strip()
    password = input("Insert password: ").strip()
    return {"server": server, "database": database, "username": username, "password": password}


def get_credentials_interactive() -> dict:
    while True:
        choice = input("Auth from env (E) or input (I)? (E/I): ").strip().upper()
        if choice == "E":
            var = input("Type variable name: ").strip()
            try:
                creds = parse_env_credentials(var)
                logging.info("Loaded credentials from environment variable '%s'", var)
                return creds
            except Exception as e:
                logging.error("%s", e)
                if input("Try again? (y/N): ").strip().lower() != "y":
                    raise
        elif choice == "I":
            return prompt_credentials()
        else:
            print("Please type 'E' or 'I'.")


def build_engine(creds: dict) -> sa.Engine:
    # Use an ODBC connection string and urlencode it to avoid issues with special chars
    odbc_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={creds['server']};"
        f"DATABASE={creds['database']};UID={creds['username']};PWD={creds['password']}"
    )
    params = urllib.parse.quote_plus(odbc_str)
    engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine


def fetch_data(engine: sa.Engine, query: str) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def save_to_sqlite(df: pd.DataFrame, path: str = DEFAULT_SQLITE, table: str = DEFAULT_TABLE):
    conn = sqlite3.connect(path)
    try:
        df.to_sql(table, conn, if_exists="replace", index=False)
    finally:
        conn.close()


def main():
    try:
        creds = get_credentials_interactive()
        engine = build_engine(creds)
        logging.info("Connecting to SQL Server and running query...")
        df = fetch_data(engine, QUERY)
        logging.info("Fetched %d rows", len(df))
        save_to_sqlite(df)
        logging.info("Saved to SQLite database '%s' table '%s'", DEFAULT_SQLITE, DEFAULT_TABLE)
        # Print a short preview instead of whole DataFrame
        print(df.head())
    except Exception as e:
        logging.error("Operation failed: %s", e)


if __name__ == "__main__":
    main()
