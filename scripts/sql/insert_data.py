import psycopg2
import os
import random
from faker import Faker
from datetime import datetime, timedelta
import logging
from utils import connect_to_db
from utils import logging_setup

logging_setup()
fake = Faker()


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


def insert_product(conn, num_records):
    if not table_exists(conn, "products"):
        logging.warning("Table 'products' does not exist. Skipping insert...")
        return
    with conn.cursor() as cur:
        for _ in range(num_records):
            cur.execute(
                """
                INSERT INTO products (product_id, product_name, category, price, stock, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    fake.uuid4(),
                    fake.word().capitalize(),
                    random.choice(["Electronics", "Clothing", "Books", "Food"]),
                    random.uniform(10, 1000),
                    random.randint(0, 1000),
                    fake.sentence(nb_words=6),
                    datetime.now(),
                    datetime.now(),
                ),
            )
    conn.commit()
    logging.info(f"Inserted {num_records} records in products table.")


def insert_transaction(conn, num_records):
    if not table_exists(conn, "transactions"):
        logging.warning("Table 'transactions' does not exist. Skipping insert...")
        return
    with conn.cursor() as cur:
        for _ in range(num_records):
            cur.execute(
                """
                INSERT INTO transactions (transaction_id, user_id, product_id, amount, transaction_type, date, description, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    fake.uuid4(),
                    fake.uuid4(),
                    fake.uuid4(),
                    random.uniform(10, 1000),
                    random.choice(["Credit", "Debit", "Purchase", "Refund"]),
                    datetime.now() - timedelta(days=random.randint(0, 365)),
                    fake.sentence(nb_words=6),
                    datetime.now(),
                ),
            )
    conn.commit()
    logging.info(f"Inserted {num_records} records in transactions table.")


def insert_user_profile(conn, num_records):
    if not table_exists(conn, "user_profiles"):
        logging.warning("Table 'user_profiles' does not exist. Skipping insert...")
        return
    with conn.cursor() as cur:
        for _ in range(num_records):
            cur.execute(
                """
                INSERT INTO user_profiles (user_id, name, username, email, address, phone_number, dob, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    fake.uuid4(),
                    fake.name(),
                    fake.user_name(),
                    fake.email(),
                    fake.address(),
                    fake.phone_number(),
                    datetime.now() - timedelta(days=random.randint(365 * 18, 365 * 80)),
                    datetime.now(),
                    datetime.now(),
                ),
            )
    conn.commit()
    logging.info(f"Inserted {num_records} records in user_profiles table.")


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    num_records = int(os.getenv("NUM_RECORDS", 10))

    # List of available insert functions
    insert_functions = [insert_product, insert_user_profile, insert_transaction]

    # Randomly select one insert function
    selected_function = random.choice(insert_functions)

    # Execute the selected function
    selected_function(conn, random.randint(1, num_records))

    conn.close()
