import os
import pandas as pd
import random
from faker import Faker
from sqlalchemy import create_engine
import logging


fake = Faker()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get the number of records to generate from an environment variable
num_records = int(os.getenv("NUM_RECORDS", 1000))  # Default to 1000 if not set
logging.info(f"Generating {num_records} records for each use case.")


# 1. Generate Fake User Profiles
def generate_user_profile():
    profile = {
        "user_id": fake.uuid4(),
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=90),
        "created_at": fake.date_time_this_decade(),
        "updated_at": pd.Timestamp.now(),
    }
    logging.debug(f"Generated user profile: {profile}")
    return profile


# 2. Generate Fake Product Data
def generate_product():
    product = {
        "product_id": fake.uuid4(),
        "product_name": fake.word().capitalize(),
        "category": random.choice(["Electronics", "Clothing", "Books", "Toys"]),
        "price": round(random.uniform(10, 1000), 2),
        "stock": random.randint(0, 500),
        "description": fake.text(max_nb_chars=200),
        "created_at": fake.date_time_this_year(),
        "updated_at": pd.Timestamp.now(),
    }
    logging.debug(f"Generated product: {product}")
    return product


# 3. Generate Fake Financial Transactions
def generate_transaction(user_ids, product_ids):
    transaction = {
        "transaction_id": fake.uuid4(),
        "user_id": random.choice(user_ids),  # Use a user_id from the user_profiles
        "product_id": random.choice(product_ids),  # Use a product_id from the products
        "amount": round(random.uniform(10, 10000), 2),
        "transaction_type": random.choice(["Credit", "Debit", "Purchase", "Refund"]),
        "date": fake.date_time_this_year(),
        "description": fake.sentence(nb_words=6),
        "updated_at": pd.Timestamp.now(),
    }
    logging.debug(f"Generated transaction: {transaction}")
    return transaction


# Generate user profiles first, so we have user_ids to link with transactions
logging.info("Starting to generate user profiles.")
user_profiles = [generate_user_profile() for _ in range(num_records)]
logging.info("Extract user_ids for foreign key relationships")
user_ids = [user["user_id"] for user in user_profiles]
logging.info("Finished generating user profiles.")

logging.info("Starting to generate products.")
products = [generate_product() for _ in range(num_records)]
logging.info("Extract product_ids for foreign key relationships")
product_ids = [product["product_id"] for product in products]
logging.info("Finished generating products.")

logging.info("Starting to generate transactions linked to user profiles and products.")
transactions = [generate_transaction(user_ids, product_ids) for _ in range(num_records)]
logging.info("Finished generating transactions.")

logging.info("Converting generated data to DataFrames.")
user_profiles_df = pd.DataFrame(user_profiles)
products_df = pd.DataFrame(products)
transactions_df = pd.DataFrame(transactions)


# Function to construct database URLs
def get_db_url(prefix):
    user = os.environ[f"POSTGRES_{prefix}_USER"]
    password = os.environ[f"POSTGRES_{prefix}_PASSWORD"]
    host = os.environ[f"POSTGRES_{prefix}_HOST"]
    db_name = os.environ[f"POSTGRES_{prefix}_DB_NAME"]
    return f"postgresql://{user}:{password}@{host}:5432/{db_name}"


# Interpolate source and target database URLs
source_db_url = get_db_url("SOURCE")
target_db_url = get_db_url("TARGET")

# Create database engines
source_engine = create_engine(source_db_url)
target_engine = create_engine(target_db_url)

# Dataframes to upload
dataframes = {
    "user_profiles": user_profiles_df,
    "products": products_df,
    "transactions": transactions_df,
}

# Upload data to both databases
for table_name, df in dataframes.items():
    try:
        df.to_sql(
            table_name, source_engine, schema="public", if_exists="replace", index=False
        )
        logging.info(f"Data uploaded to table '{table_name}' in source database.")
        df.head(0).to_sql(
            table_name,
            target_engine,
            schema="public",
            if_exists="replace",
            index=False,
            method="multi",
        )
        logging.info(f"Created empty table '{table_name}' in target database.")

    except Exception as e:
        logging.error(f"Error uploading data to PostgreSQL: {e}")
