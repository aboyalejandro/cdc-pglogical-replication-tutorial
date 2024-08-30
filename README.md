# 🔃 Change Data Capture (CDC) using pglogical plugin in PostgreSQL

Are you exploring CDC open-source solutions or just interested on checking how it works❓

This repo is a portable sample project for running CDC with pglogical plugin. In just a few commands you can test the capabilities of this built-in Postgres features and extend it as you please.

You can find pre-made scripts to run inserts, deletes and updates just by passing `NUM_RECORDS` env var to the `make` commands. Whenever you use that command, it will randomize the amount of actions between 1 and your number.


### 🙋🏻‍♂️ Pre-requesites:
- Rename `.env.example` file to `.env` and set your credentials for the databases.
- Docker Desktop

## 📝 Considerations:

- You need PRIMARY KEYs on the TABLES you want to replicate. Not views.
- `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` work properly.
- This feature doesn’t replicate sequences, DDLs or schemas. Note that the scripts were modified to adapt to pglogical plugin with some DDL commands (`CREATE TABLE`, `DROP TABLE`, `ALTER TABLE`).
- Schema changes are ignored. Adding or dropping columns will do nothing. Afterwards the replication will be broken.
- If you have set `pglogical.replication_set_add_all_tables('default', ARRAY['public']);` and you create a table, you need to also add it on the target database, otherwise it will break the replication. You need to create it on both sides to add it to replication.
- The previous point works similarly to the `DROP TABLE`, you need to remove it from the replication set and then drop it on both sides.

To run the project, you can do: 

```sh
make build
NUM_RECORDS=10000 make run #Default to 5000 if not specified
```

## 🚀 Start CDC:
Docker will start by default with the wal_level set as 'logical'. Open another terminal and run:

```sh 
make cdc-pglogical
```
This will the following things on each side:

- **Source/Publisher**
  - Check if a node exists.
  - Create pglogical extension.
  - Create a publisher node.
  - Add tables to the subscription.
- **Target/Subscriber**
  - Check if a node exists.
  - Create pglogical extension.
  - Create a subscription to the publisher.

## 🔃 Make changes:

This scripts will run `INSERT`, `UPDATE`, `DELETE` to one of the 3 generated tables on `generate_data.py`.   

```sh 
NUM_RECORDS=5 make insert-data 
NUM_RECORDS=5 make delete-data
NUM_RECORDS=5 make update-data
make truncate
```

Or you can run single commands directly on the source database if you prefer. 

## ✅ Check with queries (Source):
To query databases like to use DBeaver, but you can use VSCode or psql if you prefer. 

Validate the CDC process is OK on the Source/Publisher side. You should see the listed tables you are replicating and the slot following a pattern like `pgl_target_db_source_node_*`:

```sql
select * from pg_replication_slots;
select * from pglogical.replication_set_table;
select * from pglogical.replication_set;
```

## ✅ Check with queries (Target):

Validate the CDC is OK on the Target/Subscriber side. You should see the listed subscription:

```sql
select * from pglogical.show_subscription_status();
```
Count rows after running `INSERT` or `DELETE` in real-time:

```sql
select count(*) from products;
select count(*) from user_profiles;
select count(*) from transactions;
```
Validate after `UPDATE`:

```sql
select max(updated_at) from products;
select max(updated_at) from user_profiles;
select max(updated_at) from transactions;
```

## 🔨 Break the replication: 

Note: The scripts are limited to `TRUNCATE`, `DROP`, `INSERT`, `UPDATE` or `DELETE` `transactions`, `products` and `user_profiles`. `CREATE TABLE` will add a new table randomly. If you ended up dropping all the tables, you can do Ctrl+C and `make restart` to spin-up the project again. 

```sh
make create-table # will break the replication if you added all tables in the replication_set
make drop-table # breaks the replication if it was included in the replication_set, if not it will go on.
make add-column # will be ignored, replication will continue
```
Remember to always check on Target Database if the changes are resulting or not.

### 😎 [Follow me on Linkedin](https://www.linkedin.com/in/alejandro-aboy/)
- Get tips, learnings and tricks for your Data career!

### 📩 [Subscribe to The Pipe & The Line](https://thepipeandtheline.substack.com/?utm_source=github&utm_medium=referral)
- Join the Substack newsletter to get similar content to this one and more to improve your Data career!
