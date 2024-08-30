import psycopg2
import logging
from utils import connect_to_db, logging_setup, find_tables, is_source_database


logging_setup()


def add_table_to_replication_set(conn, table_name):
    with conn.cursor() as cur:
        try:
            # Check if pglogical extension is installed
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pglogical')"
            )
            if not cur.fetchone()[0]:
                logging.error("pglogical extension is not installed")
                return False

            # Check if the 'default' replication set exists
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM pglogical.replication_set WHERE set_name = 'default')"
            )
            if not cur.fetchone()[0]:
                logging.error("Default replication set does not exist")
                return False

            # Add the table to the replication set
            cur.execute(
                f"SELECT pglogical.replication_set_add_table('default', '{table_name}')"
            )
            logging.info(f"Added {table_name} to replication set.")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error adding table to replication set: {e}")
            return False


def create_random_table(conn):
    with conn.cursor() as cur:
        tables = {
            "stores": """
                CREATE TABLE IF NOT EXISTS stores (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """,
            "vendors": """
                CREATE TABLE IF NOT EXISTS vendors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """,
            "resellers": """
                CREATE TABLE IF NOT EXISTS resellers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """,
        }

        # Pick a random table that doesn't exist in the database
        for table_name, create_query in tables.items():
            cur.execute(
                f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='{table_name}');"
            )
            if not cur.fetchone()[0]:
                cur.execute(create_query)
                logging.info(f"Created table: {table_name}")

                # Add the table to replication set only in source
                if is_source_database(conn):
                    if add_table_to_replication_set(conn, table_name):
                        logging.info(
                            f"Successfully added {table_name} to replication set."
                        )
                    else:
                        logging.warning(
                            f"Failed to add {table_name} to replication set."
                        )
                break  # Exit after creating one table
    conn.commit()


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    create_random_table(conn)
    conn.close()
    conn = connect_to_db("TARGET")
    create_random_table(conn)
    conn.close()
    logging.info("Random table creation complete in both databases.")
