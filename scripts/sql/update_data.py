import psycopg2
import os
import random
from datetime import datetime, timedelta
import logging
from utils import connect_to_db
from utils import logging_setup

logging_setup()


def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            )
            """,
            (table_name,),
        )
        return cur.fetchone()[0]


def update_product(conn, num_records):
    if not table_exists(conn, "products"):
        logging.warning("Table 'products' does not exist. Skipping update...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT product_id FROM products ORDER BY RANDOM() LIMIT %s", (num_records,)
        )
        product_ids = cur.fetchall()
        for product_id in product_ids:
            cur.execute(
                """
                UPDATE products
                SET price = %s, stock = %s, updated_at = NOW()
                WHERE product_id = %s
            """,
                (random.uniform(10, 1000), random.randint(0, 1000), product_id[0]),
            )
    conn.commit()
    logging.info(f"Updated {num_records} records in products table.")


def update_user_profile(conn, num_records):
    if not table_exists(conn, "user_profiles"):
        logging.warning("Table 'user_profiles' does not exist. Skipping update...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id FROM user_profiles ORDER BY RANDOM() LIMIT %s",
            (num_records,),
        )
        user_ids = cur.fetchall()
        for user_id in user_ids:
            cur.execute(
                """
                UPDATE user_profiles
                SET address = %s, phone_number = %s, updated_at = NOW()
                WHERE user_id = %s
            """,
                (
                    f"{random.randint(1, 999)} New St, City, Country",
                    f"+1-555-{random.randint(1000000, 9999999)}",
                    user_id[0],
                ),
            )
    conn.commit()
    logging.info(f"Updated {num_records} records in user_profiles table.")


def update_transaction(conn, num_records):
    if not table_exists(conn, "transactions"):
        logging.warning("Table 'transactions' does not exist. Skipping update...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT transaction_id FROM transactions ORDER BY RANDOM() LIMIT %s",
            (num_records,),
        )
        transaction_ids = cur.fetchall()
        for transaction_id in transaction_ids:
            cur.execute(
                """
                UPDATE transactions
                SET amount = %s, transaction_type = %s, date = %s, description = %s, updated_at = NOW()
                WHERE transaction_id = %s
            """,
                (
                    random.uniform(10, 1000),
                    random.choice(["Purchase", "Refund", "Exchange", "Credit"]),
                    datetime.now() - timedelta(days=random.randint(0, 30)),
                    f"Updated transaction description {random.randint(1, 1000)}",
                    transaction_id[0],
                ),
            )
    conn.commit()
    logging.info(f"Updated {num_records} records in transactions table.")


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    num_records = int(os.getenv("NUM_RECORDS", 10))

    # List of available update functions
    update_functions = [update_product, update_user_profile, update_transaction]

    # Randomly select one update function
    selected_function = random.choice(update_functions)

    # Execute the selected function
    selected_function(conn, random.randint(1, num_records))

    conn.close()
