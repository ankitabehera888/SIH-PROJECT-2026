# PowerShell Script to Stop Apache Airflow Stack
$ErrorActionPreference = "Stop"

Write-Host "Stopping Healthcare Data Pipeline Airflow Stack..." -ForegroundColor Yellow
$ComposePath = Join-Path (Split-Path -Parent $PSScriptRoot) "docker\airflow\docker-compose.airflow.yml"
docker compose -f $ComposePath down
Write-Host "Airflow stack stopped successfully." -ForegroundColor Green
