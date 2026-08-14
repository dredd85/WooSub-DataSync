
# WooSub DataSync

This project compares product data from a local Subiekt database with WooCommerce product data, then helps synchronize stock levels between them.

The workflow is organized as small standalone scripts, with a main entrypoint that lets you choose which step to run.

## Project structure

- main.py - menu-based runner for the project
- extract_subiekt.py - loads data from SQL Server/Subiekt into SQLite
- fetch_woocommerce.py - fetches product data from WooCommerce and stores it in SQLite
- report_differences.py - compares WooCommerce and Subiekt data and prints summaries
- auto_update_inventory.py - updates WooCommerce stock based on the local Subiekt stock status
- DB_compare.db - SQLite database used by the comparison flow
- Old_versions/ - previous script versions kept for reference

## Database model

The project uses one SQLite database: DB_compare.db

Main tables:

- prod_subiekt
  - sku
  - name
  - stock_quantity
  - min_stock
- prod_woo
  - id
  - sku
  - name
  - stock_quantity
  - stock_status

The comparison logic matches products by SKU.

## Dependencies

Install the required Python packages:

```bash
pip install pyodbc pandas sqlalchemy woocommerce
```

Optional packages may be needed depending on your environment, especially for SQL Server ODBC access.

## Typical workflow

Run the project from the project folder:

```bash
python main.py
```

From the menu you can choose:

1. Extract Subiekt
2. Fetch WooCommerce
3. Show Reports
4. Update Inventory
5. Run all scripts

## Script responsibilities

### 1. extract_subiekt.py

- prompts for SQL Server credentials or reads them from an environment variable
- connects to the SQL Server database
- runs the Subiekt query
- saves the result into prod_subiekt inside DB_compare.db
- prints a preview of the first rows

### 2. fetch_woocommerce.py

- prompts for WooCommerce credentials or reads them from an environment variable
- connects to the WooCommerce REST API
- downloads product data
- stores it in prod_woo inside DB_compare.db
- prints a small sample of fetched products for validation

### 3. report_differences.py

- reads both SQLite tables
- compares product coverage, stock levels, and out-of-stock conditions
- prints human-readable summaries
- asks before moving to the next report section

### 4. auto_update_inventory.py

- compares local Subiekt stock versus WooCommerce stock
- identifies products that should be marked out of stock or restored to stock
- shows the products that will be updated
- asks for confirmation before applying changes
- sends updates to WooCommerce via the API

## Credential handling

The scripts support two modes:

- environment variables
- interactive input

When credentials are supplied through environment variables, the scripts expect a semicolon-separated format depending on the script.

## Notes

- This project is intentionally built as procedural scripts, not as a package.
- The database is local and intended for comparison and inventory sync work.
- The project keeps historical and older script versions in Old_versions/ for reference.

## Example usage

```bash
python main.py
```

Then select the action you want to perform from the menu.

## Future improvements

Possible next improvements include:

- better validation of database schema before updates
- more detailed logging for failed product updates
- export of comparison reports to CSV or TXT
- optional dry-run mode for inventory synchronization
