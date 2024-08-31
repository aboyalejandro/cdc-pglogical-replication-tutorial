# 🔃 Change Data Capture (CDC) using pglogical plugin in PostgreSQL

Are you exploring CDC open-source solutions or just interested on checking how it works❓

This repo is a portable sample project for running CDC with pglogical plugin. In just a few commands you can test the capabilities of this built-in Postgres features and extend it as you please.

You can find pre-made scripts to run inserts, deletes and updates just by passing `NUM_RECORDS` env var to the `make` commands. Whenever you use that command, it will randomize the amount of actions between 1 and your number.

📝 Note: This repo showcases `pglogical plugin` with some adjustments to extend basic functionality and cover some weaknesses of the software. If you prefer to see the basic behaviour with no enhancements, you can check the [CDC Logical Replication tutorial](https://github.com/aboyalejandro/cdc_logical_replication_tutorial). 

### 🙋🏻‍♂️ Pre-requesites:
- Rename `.env.example` file to `.env` and set your credentials for the databases.
- Docker Desktop

## 📝 Considerations:

- Be default, pglogical will copy an initial snapshot when enabled.
- You need PRIMARY KEYs on the TABLES you want to replicate. Not VIEWS.
- `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` commands work properly.
- This feature doesn’t replicate sequences, DDLs or schemas. 
- Schema changes are ignored. Adding or dropping columns will do nothing.
- If you have set `pglogical.replication_set_add_all_tables('default', ARRAY['public']);` and run `CREATE TABLE`, you need to also add it on the target database, otherwise it will break the replication. 
- The previous point works similarly to the `DROP TABLE`, you need to remove it from the replication set and then drop it on both sides.

## 👀 Adjustments:
- Scripts will add/remove columns to tables on source and target databases.
- Scripts will add new tables to the replication and to both databses.
- Scripts will remove tables from the replication set and drop tables on both databases.

To run the project, you can do: 

```sh
make build
NUM_RECORDS=10000 make run #Default to 5000 if not specified
```

## 🚀 Start CDC:
Docker will start by default with all the parameters configured for pglogical plugin. Open another terminal and run:

```sh 
make cdc-pglogical
```
This will apply the following things on each side:

- **Source/Publisher**
  - Check if a node exists.
  - Create pglogical extension.
  - Create a publisher node.
  - Add tables to the replication set.
- **Target/Subscriber**
  - Check if a node exists.
  - Create pglogical extension.
  - Create a subscription to the publisher.

You can run these commands to validate everything was created properly in both databases:

```sql
show wal_level; -- logical
show max_worker_processes; -- 10
show max_replication_slots; -- 10
show max_wal_senders; -- 10
show shared_preload_libraries; -- pglogical
```

## 🔃 Make changes:

These scripts will run `INSERT`, `UPDATE`, `DELETE` randomly to one of the 3 generated tables on `generate_data.py`.   

```sh 
NUM_RECORDS=5 make insert-data 
NUM_RECORDS=5 make delete-data
NUM_RECORDS=5 make update-data
make truncate
```

Or you can run single commands directly on the source database if you prefer. 

## ✅ Check with queries (Source):
To query databases like to use DBeaver, but you can use VSCode or psql if you prefer. 

Validate the CDC process is OK on the Source/Publisher side. You should see the listed tables you are replicating and the active slot named with a pattern like  this `pgl_target_db_source_node_*`:

```sql
select * from pg_replication_slots;
select * from pglogical.replication_set_table;
```

## ✅ Check with queries (Target):

Validate the CDC is OK on the Target/Subscriber side. You should see the listed subscription. 

You can always come back to this command to check if the replication is broken:

```sql
select * from pglogical.show_subscription_status();
```
Count rows after running `INSERT` or `DELETE` in real-time:

```sql
select count(*) from products;
select count(*) from user_profiles;
select count(*) from transactions;

select * from pglogical.show_subscription_status();
```
Validate after `UPDATE`:

```sql
select max(updated_at) from products;
select max(updated_at) from user_profiles;
select max(updated_at) from transactions;

select * from pglogical.show_subscription_status();
```

## 🔨 Enhanced scripts in action: 

📝 Note: With basic functionality in place, these statements would break the replicationg. 

The scripts are limited to run against `transactions`, `products` and `user_profiles` tables. 

`CREATE TABLE` will add a new table randomly. If you want to run `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` you should do it manually:

```sh
make create-table 
make drop-table 
```

You should this next to each other since the 'subtype' column will be removed:

```sh
make add-column 
make drop-column 
```

Remember to always check on Target Database if the changes are resulting or not.

If you ended up dropping all the tables, you can do Ctrl+C and `make restart` to spin-up the project again. 

### 😎 [Follow me on Linkedin](https://www.linkedin.com/in/alejandro-aboy/)
- Get tips, learnings and tricks for your Data career!

### 📩 [Subscribe to The Pipe & The Line](https://thepipeandtheline.substack.com/?utm_source=github&utm_medium=referral)
- Join the Substack newsletter to get similar content to this one and more to improve your Data career!
