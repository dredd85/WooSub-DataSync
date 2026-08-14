import logging
import os
import sqlite3
from typing import Dict, List, Tuple

import pandas as pd
from woocommerce import API

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_DB = "DB_compare.db"
DEFAULT_TABLE = "prod_woo"


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


def connect_db(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def query_df(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    return pd.read_sql(query, conn)


def load_products_to_mark_out_of_stock(conn: sqlite3.Connection) -> List[Tuple[int, str]]:
    local_df = query_df(
        conn,
        """
        SELECT sku, stock_quantity, min_stock
        FROM prod_subiekt
        WHERE min_stock > stock_quantity
        """,
    )

    woo_df = query_df(
        conn,
        """
        SELECT id, sku, stock_quantity, stock_status
        FROM prod_woo
        WHERE stock_quantity > 0 OR stock_status = 'instock'
        """,
    )

    local_skus = local_df["sku"].astype(str)
    woo_df["sku"] = woo_df["sku"].astype(str)

    products_to_update = []
    for _, product in woo_df.iterrows():
        if str(product["sku"]) in local_skus.values:
            products_to_update.append((int(product["id"]), str(product["sku"])))

    return products_to_update


def load_products_to_mark_in_stock(conn: sqlite3.Connection) -> List[Tuple[int, str, int]]:
    local_df = query_df(
        conn,
        """
        SELECT sku, stock_quantity, min_stock
        FROM prod_subiekt
        WHERE stock_quantity >= min_stock
        """,
    )

    woo_df = query_df(
        conn,
        """
        SELECT id, sku, stock_quantity, stock_status
        FROM prod_woo
        WHERE stock_quantity = 0 OR stock_status = 'outofstock'
        """,
    )

    local_df["sku"] = local_df["sku"].astype(str)
    woo_df["sku"] = woo_df["sku"].astype(str)

    products_to_update = []
    for _, item in local_df.iterrows():
        sku = str(item["sku"])
        stock_level = int(item["stock_quantity"])
        match = woo_df[woo_df["sku"] == sku]
        if not match.empty:
            product_id = int(match.iloc[0]["id"])
            new_stock_level = max(1, round(stock_level / 2) + 1)
            products_to_update.append((product_id, sku, new_stock_level))

    return products_to_update


def update_product_stock(api: API, product_id: int, sku: str, new_stock: int) -> bool:
    try:
        response = api.put(f"products/{product_id}", data={"stock_quantity": new_stock}).json()
        if "message" in response:
            logging.error("Failed to update SKU %s: %s", sku, response["message"])
            return False
        logging.info("Updated SKU %s to stock=%s", sku, new_stock)
        return True
    except Exception as e:
        logging.error("Error updating SKU %s: %s", sku, e)
        return False


def prompt_continue(message: str) -> bool:
    response = input(f"{message} (Y/n): ").strip().lower()
    return response != "n"


def preview_products(products: List[Tuple], title: str) -> None:
    print(f"\n{title}:")
    if not products:
        print("  (none)")
        return

    for item in products:
        if len(item) == 2:
            product_id, sku = item
            print(f"  Product ID={product_id} | SKU={sku} | New stock=0")
        else:
            product_id, sku, new_stock = item
            print(f"  Product ID={product_id} | SKU={sku} | New stock={new_stock}")


def run_update_batch(api: API, products: List[Tuple], target_stock: int, label: str) -> int:
    if not products:
        print(f"No products require {label}.")
        return 0

    preview_products(products, f"Products to update for {label}")
    if not prompt_continue(f"Proceed with {label} update?"):
        print(f"{label.title()} update cancelled.")
        return 0

    success_count = 0
    for item in products:
        if len(item) == 2:
            product_id, sku = item
            new_stock = target_stock
            print(f"Updating SKU={sku} | Product ID={product_id} | New stock={new_stock}")
            if update_product_stock(api, product_id, sku, new_stock):
                success_count += 1
        else:
            product_id, sku, new_stock = item
            print(f"Updating SKU={sku} | Product ID={product_id} | New stock={new_stock}")
            if update_product_stock(api, product_id, sku, new_stock):
                success_count += 1

    print(f"{label.title()} update complete. Updated successfully: {success_count}/{len(products)}")
    return success_count


def main() -> None:
    try:
        print("\n" + "=" * 70)
        print("WooCommerce stock sync")
        print("=" * 70)

        conn = connect_db()
        creds = get_credentials_interactive()
        api = build_api_client(creds)

        print("\nChecking products that should be marked out of stock...")
        products_to_set_out_of_stock = load_products_to_mark_out_of_stock(conn)
        run_update_batch(api, products_to_set_out_of_stock, 0, "out-of-stock")

        print("\nChecking products that should be marked in stock...")
        products_to_set_in_stock = load_products_to_mark_in_stock(conn)
        run_update_batch(api, products_to_set_in_stock, 0, "in-stock")

        conn.close()
        print("\n" + "=" * 70)
        print("Finished WooCommerce stock sync.")
        print("=" * 70)

    except Exception as e:
        logging.error("Operation failed: %s", e)


if __name__ == "__main__":
    main()
