import psycopg2
import logging
import os
import time
from sql.utils import connect_to_db
from sql.utils import logging_setup

logging_setup()


def check_pglogical_setup(conn, node_name):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pglogical';")
        extension_exists = cur.fetchone()[0] > 0
        cur.execute(
            "SELECT COUNT(*) FROM pglogical.node WHERE node_name = %s;", (node_name,)
        )
        node_exists = cur.fetchone()[0] > 0
    return extension_exists and node_exists


def setup_pglogical(db, conn):
    with conn.cursor() as cur:
        db = db.lower()
        node_name = f"{db}_node"
        logging.info(f"Setting up pglogical on {db.upper()} node...")
        try:
            # Create pglogical extension if not exists
            cur.execute("CREATE EXTENSION IF NOT EXISTS pglogical;")

            # Create node
            cur.execute(
                f"SELECT pglogical.create_node(node_name := '{node_name}', dsn := 'host={db}_db port=5432 dbname={os.environ[f'POSTGRES_{db.upper()}_DB_NAME']} user={os.environ[f'POSTGRES_{db.upper()}_USER']} password={os.environ[f'POSTGRES_{db.upper()}_PASSWORD']}');"
            )

            if db == "source":
                # Add all tables to the replication set
                cur.execute(
                    "SELECT pglogical.replication_set_add_all_tables('default', ARRAY['public']);"
                )
            else:
                # Create subscription on target
                subscription_name = "pglogical_subscription"
                provider_dsn = f"host=source_db port=5432 dbname={os.environ['POSTGRES_SOURCE_DB_NAME']} user={os.environ['POSTGRES_SOURCE_USER']} password={os.environ['POSTGRES_SOURCE_PASSWORD']}"
                cur.execute(
                    f"SELECT pglogical.create_subscription(subscription_name := '{subscription_name}', provider_dsn := %s);",
                    (provider_dsn,),
                )

            conn.commit()
            logging.info(f"Successfully set up pglogical on {db.upper()} node.")
        except Exception as e:
            logging.error(f"Error setting up pglogical on {db.upper()} node: {e}")
            conn.rollback()


def wait_for_pglogical_setup(db):
    conn = connect_to_db(db.upper())
    node_name = f"{db.lower()}_node"
    while not check_pglogical_setup(conn, node_name):
        logging.info(f"Waiting for pglogical setup on {db.upper()} node...")
        time.sleep(5)
    conn.close()


if __name__ == "__main__":
    # Set up source database
    conn_source = connect_to_db("SOURCE")
    setup_pglogical("source", conn_source)
    conn_source.close()

    # Wait for source setup to complete
    wait_for_pglogical_setup("source")

    # Set up target database
    conn_target = connect_to_db("TARGET")
    setup_pglogical("target", conn_target)
    conn_target.close()

    # Wait for target setup to complete
    wait_for_pglogical_setup("target")

    logging.info(
        "pglogical setup completed successfully on both source and target databases."
    )
