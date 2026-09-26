# PowerShell Script to Reset Apache Airflow Metadata Database
$ErrorActionPreference = "Stop"

Write-Host "Resetting Airflow Metadata Database..." -ForegroundColor Yellow
$ComposePath = Join-Path (Split-Path -Parent $PSScriptRoot) "docker\airflow\docker-compose.airflow.yml"
docker compose -f $ComposePath down -v

docker exec -i healthcare_postgres psql -U healthcare -d postgres -c "DROP DATABASE IF EXISTS airflow_db;"
docker exec -i healthcare_postgres psql -U healthcare -d postgres -c "CREATE DATABASE airflow_db;"

Write-Host "Airflow metadata database reset complete." -ForegroundColor Green
