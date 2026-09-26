# PowerShell Script to Start Apache Airflow Stack
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Starting Healthcare Data Pipeline Airflow Stack..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Ensure separate metadata database airflow_db exists in postgres container
Write-Host "[1/3] Ensuring separate 'airflow_db' database exists..." -ForegroundColor Yellow
docker exec -i healthcare_postgres psql -U healthcare -d postgres -c "SELECT 1 FROM pg_database WHERE datname = 'airflow_db';" | Out-Null
if ($LASTEXITCODE -ne 0) {
    docker exec -i healthcare_postgres psql -U healthcare -d postgres -c "CREATE DATABASE airflow_db;"
    Write-Host "Created 'airflow_db' metadata database." -ForegroundColor Green
} else {
    Write-Host "'airflow_db' already exists." -ForegroundColor Green
}

# 2. Build and run Airflow services
Write-Host "[2/3] Building and starting Airflow Webserver & Scheduler containers..." -ForegroundColor Yellow
$ComposePath = Join-Path (Split-Path -Parent $PSScriptRoot) "docker\airflow\docker-compose.airflow.yml"
docker compose -f $ComposePath up -d

# 3. Check health and print access URLs
Write-Host "[3/3] Verifying Airflow service status..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
docker ps --filter "name=healthcare_airflow"

Write-Host "==================================================" -ForegroundColor Green
Write-Host "Airflow Web UI:   http://localhost:8080" -ForegroundColor Green
Write-Host "Username:         admin" -ForegroundColor Green
Write-Host "Password:         admin" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
