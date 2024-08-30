import psycopg2
import os
import logging
import random
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


def delete_products(conn, num_records):
    if not table_exists(conn, "products"):
        logging.warning("Table 'products' does not exist. Skipping delete...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM products WHERE product_id IN (SELECT product_id FROM products ORDER BY RANDOM() LIMIT %s)",
            (num_records,),
        )
    conn.commit()
    logging.info(f"Deleted {num_records} records in products table.")


def delete_transactions(conn, num_records):
    if not table_exists(conn, "transactions"):
        logging.warning("Table 'transactions' does not exist. Skipping delete...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM transactions WHERE transaction_id IN (SELECT transaction_id FROM transactions ORDER BY RANDOM() LIMIT %s)",
            (num_records,),
        )
    conn.commit()
    logging.info(f"Deleted {num_records} records in transactions table.")


def delete_user_profiles(conn, num_records):
    if not table_exists(conn, "user_profiles"):
        logging.warning("Table 'user_profiles' does not exist. Skipping delete...")
        return
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_profiles WHERE user_id IN (SELECT user_id FROM user_profiles ORDER BY RANDOM() LIMIT %s)",
            (num_records,),
        )
    conn.commit()
    logging.info(f"Deleted {num_records} records in user_profiles table.")


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    num_records = int(os.getenv("NUM_RECORDS", 10))

    # List of available delete functions
    delete_functions = [delete_products, delete_user_profiles, delete_transactions]

    # Randomly select one delete function
    selected_function = random.choice(delete_functions)

    # Execute the selected function
    selected_function(conn, random.randint(1, num_records))

    conn.close()
