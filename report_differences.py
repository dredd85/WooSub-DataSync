import logging
import sqlite3

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_DB = "DB_compare.db"
WOO_TABLE = "prod_woo"
SUB_TABLE = "prod_subiekt"


def connect_db(db_path: str = DEFAULT_DB):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)


def query_df(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    """Execute a SQL query and return a pandas DataFrame."""
    return pd.read_sql(query, conn)


def report_products_summary(conn: sqlite3.Connection) -> None:
    """Report: Compare product inventory between WooCommerce and Subiekt."""
    print("\n" + "=" * 70)
    print("Report: Products for Ecommerce Summary")
    print("=" * 70)

    overall_woo = query_df(
        conn, f"SELECT sku, name FROM {WOO_TABLE}"
    )
    overall_sub = query_df(
        conn, f"SELECT sku, name FROM {SUB_TABLE}"
    )

    total_woo = len(overall_woo)
    total_sub = len(overall_sub)

    print(f"Total products in WooCommerce: {total_woo}")
    print(f"Total products in Subiekt: {total_sub}")
    print()

    woo_symbols = set(overall_woo["sku"])
    sub_symbols = set(overall_sub["sku"])

    woo_not_in_sub = overall_woo[~overall_woo["sku"].isin(sub_symbols)]
    sub_not_in_woo = overall_sub[~overall_sub["sku"].isin(woo_symbols)]

    print(f"Products in WooCommerce but not in Subiekt: {len(woo_not_in_sub)}")
    for _, product in woo_not_in_sub.iterrows():
        print(f"  SKU: {product['sku']} - Name: {product['name']}")

    print()
    print(f"Products in Subiekt but not in WooCommerce: {len(sub_not_in_woo)}")
    for _, product in sub_not_in_woo.iterrows():
        print(f"  SKU: {product['sku']} - Name: {product['name']}")


def report_out_of_stock(conn: sqlite3.Connection) -> None:
    """Report: Compare out-of-stock status between WooCommerce and Subiekt."""
    print("\n" + "=" * 70)
    print("Report: Out Of Stock Summary")
    print("=" * 70)

    out_of_stock_sub = query_df(
        conn,
        f"SELECT sku, name FROM {SUB_TABLE} WHERE min_stock > stock_quantity"
    )

    out_of_stock_woo = query_df(
        conn,
        f"SELECT sku, name FROM {WOO_TABLE} WHERE stock_quantity <= 0 OR stock_status = 'outofstock'"
    )

    total_oos_sub = len(out_of_stock_sub)
    total_oos_woo = len(out_of_stock_woo)

    print(f"Total products out of stock in WooCommerce: {total_oos_woo}")
    print(f"Total products out of stock in Subiekt: {total_oos_sub}")
    print()

    sub_symbols = set(out_of_stock_sub["sku"])
    woo_symbols = set(out_of_stock_woo["sku"])

    oos_sub_not_in_woo = out_of_stock_sub[~out_of_stock_sub["sku"].isin(woo_symbols)]
    oos_woo_not_in_sub = out_of_stock_woo[~out_of_stock_woo["sku"].isin(sub_symbols)]

    if len(oos_sub_not_in_woo) > 0:
        print(
            f"Out of stock in Subiekt but In Stock in WooCommerce: {len(oos_sub_not_in_woo)}"
        )
        for _, product in oos_sub_not_in_woo.iterrows():
            print(f"  SKU: {product['sku']} - Name: {product['name']}")
        print("\n⚠ Run the auto_update_inventory script to sync these products.")
    else:
        print("✓ No products to set out of stock in WooCommerce.")

    print()

    if len(oos_woo_not_in_sub) > 0:
        print(
            f"Out of stock in WooCommerce but In Stock in Subiekt: {len(oos_woo_not_in_sub)}"
        )
        for _, product in oos_woo_not_in_sub.iterrows():
            print(f"  SKU: {product['sku']} - Name: {product['name']}")
        print("\n⚠ Manually update stock in WooCommerce to sync.")
    else:
        print("✓ No products to update in Subiekt.")


def report_stock_comparison(conn: sqlite3.Connection) -> None:
    """Report: Compare stock quantities between WooCommerce and Subiekt."""
    print("\n" + "=" * 70)
    print("Report: Stock Comparison Summary")
    print("=" * 70)

    sub_lower = query_df(
        conn,
        f"""
        SELECT woo.name, woo.sku, woo.stock_quantity as woo_stock, sub.stock_quantity as sub_stock
        FROM {WOO_TABLE} woo
        JOIN {SUB_TABLE} sub ON woo.sku = sub.sku
        WHERE sub.stock_quantity < woo.stock_quantity
          AND woo.stock_status != 'outofstock'
        """
    )

    woo_lower = query_df(
        conn,
        f"""
        SELECT woo.name, woo.sku, woo.stock_quantity as woo_stock, sub.stock_quantity as sub_stock
        FROM {WOO_TABLE} woo
        JOIN {SUB_TABLE} sub ON woo.sku = sub.sku
        WHERE sub.stock_quantity > woo.stock_quantity
          AND woo.stock_status = 'outofstock'
        """
    )

    print("Products with low stock in Subiekt (higher in WooCommerce):")
    if len(sub_lower) > 0:
        print(sub_lower.to_string(index=False))
    else:
        print("  (none)")

    print()
    print("Products with higher stock in Subiekt (out of stock in WooCommerce):")
    if len(woo_lower) > 0:
        print(woo_lower.to_string(index=False))
    else:
        print("  (none)")


def prompt_continue(message: str = "Proceed to next report?") -> bool:
    """Prompt user to continue or stop."""
    response = input(f"\n{message} (Y/n): ").strip().lower()
    return response != "n"


def main() -> None:
    """Run all reports interactively."""
    try:
        conn = connect_db()
        logging.info("Connected to database '%s'", DEFAULT_DB)

        report_products_summary(conn)

        if not prompt_continue("Proceed with Out Of Stock Summary?"):
            print("Exiting.")
            conn.close()
            return

        report_out_of_stock(conn)

        if not prompt_continue("Proceed with Stock Comparison Summary?"):
            print("Exiting.")
            conn.close()
            return

        report_stock_comparison(conn)

        print("\n" + "=" * 70)
        print("All reports completed.")
        print("=" * 70)

        conn.close()
    except Exception as e:
        logging.error("Operation failed: %s", e)


if __name__ == "__main__":
    main()