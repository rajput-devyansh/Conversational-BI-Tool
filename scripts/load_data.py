import sqlite3
import pandas as pd
from pathlib import Path

RAW_DATA_DIR = Path("data/raw/Brazilian_ECommerce_Olist")
DB_PATH = Path("data/Brazilian_ECommerce_Olist.db")

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "category_name_translation": "product_category_name_translation.csv",
}

def load_csvs_to_sqlite():
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_DIR}"
        )

    conn = sqlite3.connect(DB_PATH)

    for table_name, csv_file in TABLES.items():
        csv_path = RAW_DATA_DIR / csv_file

        if not csv_path.exists():
            raise FileNotFoundError(f"Missing file: {csv_path}")

        print(f"Loading {csv_file} → table '{table_name}'")

        df = pd.read_csv(csv_path)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",  # idempotent
            index=False
        )

        print(f"  Loaded {len(df)} rows")

    conn.close()
    print("✅ Database created successfully")

if __name__ == "__main__":
    load_csvs_to_sqlite()