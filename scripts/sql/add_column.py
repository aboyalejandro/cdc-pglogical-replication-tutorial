import psycopg2
import random
import logging
from utils import connect_to_db, logging_setup, find_tables

logging_setup()


def get_random_table(conn):
    with conn.cursor() as cur:
        cur.execute(find_tables())
        tables = cur.fetchall()
        if not tables:
            return None
        return random.choice(tables)[0]


def table_exists(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT to_regclass('public.{table_name}')")
        return cur.fetchone()[0] is not None


def column_exists(conn, table_name, column_name):
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}';
        """
        )
        return cur.fetchone() is not None


def add_column_to_table(conn, table_name, column_name):
    if not table_exists(conn, table_name):
        logging.warning(f"Table '{table_name}' does not exist in this database.")
        return False

    if column_exists(conn, table_name, column_name):
        logging.info(f"Column '{column_name}' already exists in table: {table_name}")
        return True

    with conn.cursor() as cur:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(255);")
        conn.commit()
        logging.info(f"Added column '{column_name}' to table: {table_name}")
        return True


def add_column_to_both_databases(source_conn, target_conn):
    # Get a random table from the SOURCE database
    table_to_alter = get_random_table(source_conn)

    if table_to_alter is None:
        logging.info("No tables found in SOURCE database to add a column.")
        return

    column_name = "subtype"

    # Add column to SOURCE database
    source_success = add_column_to_table(source_conn, table_to_alter, column_name)

    # Add column to TARGET database
    target_success = add_column_to_table(target_conn, table_to_alter, column_name)

    if source_success and target_success:
        logging.info(
            f"Successfully added column '{column_name}' to table '{table_to_alter}' in both databases."
        )
    elif source_success:
        logging.warning(
            f"Added column '{column_name}' to table '{table_to_alter}' only in SOURCE database."
        )
    elif target_success:
        logging.warning(
            f"Added column '{column_name}' to table '{table_to_alter}' only in TARGET database."
        )
    else:
        logging.error(
            f"Failed to add column '{column_name}' to table '{table_to_alter}' in both databases."
        )


if __name__ == "__main__":
    source_conn = connect_to_db("SOURCE")
    target_conn = connect_to_db("TARGET")

    add_column_to_both_databases(source_conn, target_conn)

    source_conn.close()
    target_conn.close()
