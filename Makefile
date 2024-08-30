# Check if docker-compose is available, otherwise use docker compose
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

# Run the Docker services
run:
	docker compose up --build

# Stop the Docker services
stop:
	$(DOCKER_COMPOSE) down --volumes

# Clean Docker containers, images, and volumes
clean: stop
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans

# Clean Docker container, build and runs again
restart: stop
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
	docker compose build
	docker compose up

# Insert data into the source database
insert-data:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/insert_data.py

# Update data in the source database
update-data:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/update_data.py

# Delete data from the source database
delete-data:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/delete_data.py

# Truncate a table from the source database
truncate:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/truncate_table.py

# Creates a table in the source database
create-table:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/create_table.py

# Drops a table from the source database
drop-table:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/drop_table.py

# Adds a column to a table from the source database
add-column:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/sql/add_column.py

# Enables CDC with pglogical for both nodes
cdc-pglogical:
	$(DOCKER_COMPOSE) run --rm cdc_scripts python /app/scripts/cdc_pglogical_plugin.py