import psycopg2
import random
import logging
from utils import connect_to_db
from utils import logging_setup
from utils import find_tables

logging_setup()


def add_column_to_random_table(conn):
    with conn.cursor() as cur:
        # Query to get all user-created tables in the public schema
        cur.execute(find_tables())
        tables = cur.fetchall()

        if not tables:
            logging.info("No tables found to add a column.")
            return

        # Randomly select one table from the list
        table_to_alter = random.choice(tables)[0]

        # Check if the "subtype" column already exists
        cur.execute(
            f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table_to_alter}' AND column_name = 'subtype';
        """
        )
        column_exists = cur.fetchone()

        if column_exists:
            logging.info(f"Column 'subtype' already exists in table: {table_to_alter}")
        else:
            # Add the 'subtype' column to the selected table
            cur.execute(
                f"ALTER TABLE {table_to_alter} ADD COLUMN subtype VARCHAR(255);"
            )
            logging.info(f"Added column 'subtype' to table: {table_to_alter}")

    conn.commit()


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    add_column_to_random_table(conn)
    conn.close()
    conn = connect_to_db("TARGET")
    add_column_to_random_table(conn)
    conn.close()
