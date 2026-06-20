import logging
import os
import sqlite3
from typing import Dict

from woocommerce import API

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_DB = "DB_compare.db"
DEFAULT_TABLE = "prod_woo"
SAMPLE_SIZE = 5


def parse_env_credentials(var_name: str) -> Dict[str, str]:
    cred = os.getenv(var_name)
    if not cred:
        raise ValueError(f"Environment variable '{var_name}' is not set")

    parts = [part.strip() for part in cred.split(";")]
    if len(parts) < 3:
        raise ValueError(f"Environment variable '{var_name}' is malformed")

    return {
        "url": parts[0],
        "consumer_key": parts[1],
        "consumer_secret": parts[2],
    }


def prompt_credentials() -> Dict[str, str]:
    return {
        "url": input("Insert WooCommerce site URL: ").strip(),
        "consumer_key": input("Insert consumer key: ").strip(),
        "consumer_secret": input("Insert consumer secret: ").strip(),
    }


def get_credentials_interactive() -> Dict[str, str]:
    while True:
        choice = input("Auth from env (E) or input (I)? (E/I): ").strip().upper()
        if choice == "E":
            var = input("Type variable name: ").strip()
            try:
                creds = parse_env_credentials(var)
                logging.info("Loaded WooCommerce credentials from '%s'", var)
                return creds
            except Exception as e:
                logging.error("%s", e)
                if input("Try again? (y/N): ").strip().lower() != "y":
                    raise
        elif choice == "I":
            return prompt_credentials()
        else:
            print("Please type 'E' or 'I'.")


def build_api_client(creds: Dict[str, str]) -> API:
    return API(
        creds["url"],
        creds["consumer_key"],
        creds["consumer_secret"],
        version="wc/v3",
        timeout=15,
    )


def create_table(conn: sqlite3.Connection, table_name: str = DEFAULT_TABLE) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(
        f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY,
            sku TEXT,
            name TEXT,
            stock_quantity INTEGER,
            stock_status TEXT
        )
        """
    )
    conn.commit()


def fetch_products(api: API, stock_status: str, per_page: int = 100):
    page = 1
    fetched_count = 0
    all_products = []

    while True:
        response = api.get(
            "products",
            params={
                "per_page": per_page,
                "page": page,
                "stock_status": stock_status,
            },
        )
        response.raise_for_status()
        products = response.json()

        if not products:
            logging.info("Finished fetching %s products", stock_status)
            break

        all_products.extend(products)
        fetched_count += len(products)
        logging.info("Fetched page %s for %s (%s items)", page, stock_status, len(products))
        page += 1

    return all_products


def save_products_to_db(products, table_name: str = DEFAULT_TABLE, db_path: str = DEFAULT_DB) -> None:
    records = [
        (
            int(item.get("id") or 0),
            item.get("sku") or "",
            item.get("name") or "",
            int(item.get("stock_quantity") or 0),
            item.get("stock_status") or "",
        )
        for item in products
    ]

    with sqlite3.connect(db_path) as conn:
        create_table(conn, table_name)
        conn.executemany(
            f"""
            INSERT INTO {table_name} (id, sku, name, stock_quantity, stock_status)
            VALUES (?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()

        # Read a few rows back from the database for a quick verification preview.
        sample_rows = conn.execute(
            f"SELECT id, sku, name, stock_quantity, stock_status FROM {table_name} LIMIT {SAMPLE_SIZE}"
        ).fetchall()

    print("\nSample products from database:")
    for row in sample_rows:
        print(
            f"ID={row[0]} | SKU={row[1]} | Name={row[2]} | "
            f"Stock={row[3]} | Status={row[4]}"
        )


def main() -> None:
    try:
        creds = get_credentials_interactive()
        api = build_api_client(creds)

        products = []
        for status in ("instock", "outofstock"):
            products.extend(fetch_products(api, status))

        save_products_to_db(products)

        logging.info("Saved %d products to %s", len(products), DEFAULT_TABLE)
    except Exception as e:
        logging.error("Operation failed: %s", e)


if __name__ == "__main__":
    main()