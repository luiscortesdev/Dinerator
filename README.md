# Dinerator

Apply schema to docker container using this command
```bash
Get-Content database/schema.sql | docker exec -i dinerator_postgres_db psql -U postgres -d dinerator
```