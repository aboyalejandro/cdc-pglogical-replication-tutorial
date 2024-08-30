import psycopg2
import os
import logging


def connect_to_db(db: str):
    return psycopg2.connect(
        dbname=os.environ[f"POSTGRES_{db}_DB_NAME"],
        user=os.environ[f"POSTGRES_{db}_USER"],
        password=os.environ[f"POSTGRES_{db}_PASSWORD"],
        host=os.environ[f"POSTGRES_{db}_HOST"],
        port=5432,
    )


def logging_setup():
    return logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def find_tables():
    return """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """


def is_source_database(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        return db_name == os.environ["POSTGRES_SOURCE_DB_NAME"]
