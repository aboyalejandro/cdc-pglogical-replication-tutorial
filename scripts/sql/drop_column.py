import psycopg2
import logging
from utils import connect_to_db, logging_setup, find_tables

logging_setup()


def find_table_with_subtype(cur):
    cur.execute(find_tables())
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        if column_exists(cur, table_name, "subtype"):
            return table_name

    return None


def column_exists(cur, table, column):
    cur.execute(
        f"""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = '{table}' AND column_name = '{column}';
    """
    )
    return cur.fetchone() is not None


def drop_column(cur, table, column):
    cur.execute(f"ALTER TABLE {table} DROP COLUMN {column};")
    logging.info(f"Dropped column '{column}' from table: {table}")


def drop_column_from_table(conn, table, column):
    with conn.cursor() as cur:
        if column_exists(cur, table, column):
            drop_column(cur, table, column)
        else:
            logging.info(f"Column '{column}' does not exist in table: {table}")
    conn.commit()


if __name__ == "__main__":
    source_conn = connect_to_db("SOURCE")
    target_conn = connect_to_db("TARGET")

    with source_conn.cursor() as cur:
        table_to_alter = find_table_with_subtype(cur)

    if table_to_alter:
        column_to_drop = "subtype"
        drop_column_from_table(source_conn, table_to_alter, column_to_drop)
        drop_column_from_table(target_conn, table_to_alter, column_to_drop)
        logging.info(
            f"Dropped 'subtype' column from table '{table_to_alter}' in both databases"
        )
    else:
        logging.info("No table found with 'subtype' column")

    source_conn.close()
    target_conn.close()
