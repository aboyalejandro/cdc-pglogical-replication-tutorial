import psycopg2
import logging
from sql.utils import connect_to_db
from sql.utils import logging_setup

logging_setup()


def add_id_column(conn, db):
    with conn.cursor() as cur:
        # Get the list of tables in the database
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = cur.fetchall()

        for table in tables:
            table_name = table[0]
            try:
                # Check if the ID column already exists
                cur.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s AND column_name = 'id'
                """,
                    (table_name,),
                )
                if cur.fetchone() is None:
                    # Add ID column and set it as PRIMARY KEY
                    cur.execute(
                        f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN id SERIAL PRIMARY KEY;
                    """
                    )
                    logging.info(
                        f"Added 'id' column to table '{table_name}' and set it as PRIMARY KEY in {db} database."
                    )
                else:
                    logging.info(f"'id' column already exists in table '{table_name}'.")

                # Commit changes after altering table
                conn.commit()
            except Exception as e:
                logging.error(f"Error modifying table '{table_name}': {e}")
                conn.rollback()


if __name__ == "__main__":
    conn = connect_to_db("SOURCE")
    add_id_column(conn, "SOURCE")
    conn.close()
    conn = connect_to_db("TARGET")
    add_id_column(conn, "TARGET")
    conn.close()
