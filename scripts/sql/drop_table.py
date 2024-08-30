import psycopg2
import logging
import random
import os
from utils import connect_to_db, logging_setup, find_tables, is_source_database

logging_setup()


def remove_table_from_replication_set(conn, table_name):
    if not is_source_database(conn):
        logging.info(
            f"Skipping replication set removal for {table_name} as this is not the SOURCE database."
        )
        return True

    with conn.cursor() as cur:
        try:
            # Check if pglogical extension is installed
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pglogical')"
            )
            if not cur.fetchone()[0]:
                logging.error("pglogical extension is not installed on SOURCE database")
                return False

            # Check if the table is in any replication set
            cur.execute(
                f"SELECT set_name FROM pglogical.tables WHERE relid = '{table_name}'::regclass"
            )
            replication_sets = cur.fetchall()

            if not replication_sets:
                logging.info(
                    f"Table {table_name} is not in any replication set in SOURCE database."
                )
                return True

            # Remove the table from all replication sets it's in
            for set_name in replication_sets:
                cur.execute(
                    f"SELECT pglogical.replication_set_remove_table('{set_name[0]}', '{table_name}')"
                )
                logging.info(
                    f"Removed {table_name} from replication set {set_name[0]} in SOURCE database."
                )

            return True
        except psycopg2.Error as e:
            logging.error(
                f"Error removing table from replication set in SOURCE database: {e}"
            )
            return False


def get_common_tables(source_conn, target_conn):
    with source_conn.cursor() as source_cur, target_conn.cursor() as target_cur:
        source_cur.execute(find_tables())
        target_cur.execute(find_tables())

        source_tables = set(table[0] for table in source_cur.fetchall())
        target_tables = set(table[0] for table in target_cur.fetchall())

        return list(source_tables.intersection(target_tables))


def drop_random_table(source_conn, target_conn):
    common_tables = get_common_tables(source_conn, target_conn)

    if not common_tables:
        logging.info("No common tables found to drop.")
        return

    table_to_drop = random.choice(common_tables)

    # Remove table from replication set in the source database
    if remove_table_from_replication_set(source_conn, table_to_drop):
        logging.info(
            f"Successfully handled replication set removal for {table_to_drop} in SOURCE database."
        )
    else:
        logging.warning(
            f"Failed to handle replication set removal for {table_to_drop} in SOURCE database. Proceeding with drop anyway."
        )

    # Drop the table from both databases
    for conn, db_type in [(source_conn, "SOURCE"), (target_conn, "TARGET")]:
        with conn.cursor() as cur:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table_to_drop} CASCADE;")
                conn.commit()
                logging.info(f"Dropped table: {table_to_drop} from {db_type}")
            except psycopg2.Error as e:
                conn.rollback()
                logging.error(f"Error dropping {table_to_drop} from {db_type}: {e}")


if __name__ == "__main__":
    source_conn = connect_to_db("SOURCE")
    target_conn = connect_to_db("TARGET")

    drop_random_table(source_conn, target_conn)

    source_conn.close()
    target_conn.close()

    logging.info("Table dropping process completed.")
